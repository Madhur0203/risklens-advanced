from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from app.utils.text_signals import extract_text_signals
from app.utils.recommendations import recommend_action

NUMERIC_FEATURES = [
    "amount",
    "quantity",
    "delay_days",
    "document_completeness",
    "vendor_incident_rate",
    "route_rarity",
    "cost_spike",
    "exception_count",
    "text_signal_score",
]
CATEGORICAL_FEATURES = ["vendor", "carrier", "port", "route", "filing_status"]


@dataclass
class EngineArtifacts:
    anomaly_model: IsolationForest
    predictive_model: Pipeline
    feature_importances: dict[str, float]


class RiskEngine:
    def __init__(self):
        self.artifacts: EngineArtifacts | None = None

    def _compute_rule_score(self, row: pd.Series) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []
        if row["delay_days"] >= 2:
            score += min(row["delay_days"] * 4, 20)
            reasons.append(f"Late filing ({row['delay_days']} days)")
        if row["document_completeness"] < 80:
            gap = 80 - row["document_completeness"]
            score += min(gap * 0.9, 20)
            reasons.append("Low document completeness")
        if row["vendor_incident_rate"] > 0.35:
            score += row["vendor_incident_rate"] * 18
            reasons.append("Vendor history shows repeated incidents")
        if row["route_rarity"] > 0.40:
            score += row["route_rarity"] * 14
            reasons.append("Route pattern is rare / unusual")
        if row["cost_spike"] > 0.25:
            score += row["cost_spike"] * 14
            reasons.append("Material / freight cost spike detected")
        if row["exception_count"] >= 2:
            score += row["exception_count"] * 3.8
            reasons.append("Multiple exceptions recorded")
        return min(score, 55.0), reasons

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        scores, buckets, all_evidence = [], [], []
        for text in out["notes"].fillna(""):
            score, bucket_counts, evidence = extract_text_signals(text)
            scores.append(score)
            buckets.append(json.dumps(bucket_counts))
            all_evidence.append(evidence)
        out["text_signal_score"] = scores
        out["text_signal_buckets"] = buckets
        out["text_evidence"] = all_evidence
        return out

    def train(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare(df)

        rule_scores = []
        reasons_col = []
        for _, row in df.iterrows():
            rule_score, reasons = self._compute_rule_score(row)
            reasons.extend(row["text_evidence"])
            rule_scores.append(rule_score)
            reasons_col.append(reasons)
        df["rule_score"] = rule_scores
        df["base_reasons"] = reasons_col

        anomaly_model = IsolationForest(
            n_estimators=220,
            contamination=0.12,
            random_state=42
        )
        anomaly_X = df[NUMERIC_FEATURES].copy()
        anomaly_model.fit(anomaly_X)
        raw_anomaly = -anomaly_model.score_samples(anomaly_X)
        anomaly_scaled = 100 * (raw_anomaly - raw_anomaly.min()) / (raw_anomaly.max() - raw_anomaly.min() + 1e-9)
        df["anomaly_score"] = anomaly_scaled.round(2)

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ]), NUMERIC_FEATURES),
                ("cat", Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore"))
                ]), CATEGORICAL_FEATURES)
            ]
        )
        model = GradientBoostingClassifier(random_state=42)
        predictive_model = Pipeline(
            steps=[
                ("prep", preprocessor),
                ("model", model)
            ]
        )
        predictive_model.fit(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES], df["label_escalated"])
        predictive_score = predictive_model.predict_proba(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1] * 100
        df["predictive_score"] = predictive_score.round(2)

        final_score = (
            df["rule_score"] * 0.38
            + df["anomaly_score"] * 0.22
            + df["predictive_score"] * 0.28
            + df["text_signal_score"] * 0.12
        ).clip(0, 100)
        df["final_risk_score"] = final_score.round(2)
        df["escalation_probability"] = (df["predictive_score"] / 100).round(3)
        df["severity"] = pd.cut(
            df["final_risk_score"],
            bins=[-1, 30, 55, 75, 100],
            labels=["Low", "Moderate", "High", "Critical"]
        ).astype(str)

        feature_importances = {f: 0.0 for f in NUMERIC_FEATURES}
        try:
            feature_importances = {
                feature: float(importance)
                for feature, importance in zip(NUMERIC_FEATURES, model.feature_importances_[:len(NUMERIC_FEATURES)])
            }
        except Exception:
            pass

        recommendations = []
        detailed_reasons = []
        for _, row in df.iterrows():
            reasons = list(row["base_reasons"])
            if row["anomaly_score"] >= 70:
                reasons.append("Statistically anomalous case pattern")
            if row["predictive_score"] >= 75:
                reasons.append("High escalation likelihood from predictive model")
            rec = recommend_action(row["severity"], reasons)
            recommendations.append(rec)
            detailed_reasons.append(json.dumps(reasons))
        df["recommendation"] = recommendations
        df["reasons"] = detailed_reasons

        self.artifacts = EngineArtifacts(
            anomaly_model=anomaly_model,
            predictive_model=predictive_model,
            feature_importances=feature_importances
        )
        return df

    def score_new(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.artifacts:
            raise RuntimeError("Risk engine is not trained yet.")
        df = self.prepare(df)

        rule_scores = []
        reasons_col = []
        for _, row in df.iterrows():
            rule_score, reasons = self._compute_rule_score(row)
            reasons.extend(row["text_evidence"])
            rule_scores.append(rule_score)
            reasons_col.append(reasons)
        df["rule_score"] = rule_scores
        df["base_reasons"] = reasons_col

        raw_anomaly = -self.artifacts.anomaly_model.score_samples(df[NUMERIC_FEATURES])
        anomaly_scaled = 100 * (raw_anomaly - raw_anomaly.min()) / (raw_anomaly.max() - raw_anomaly.min() + 1e-9)
        df["anomaly_score"] = anomaly_scaled.round(2)
        predictive_score = self.artifacts.predictive_model.predict_proba(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1] * 100
        df["predictive_score"] = predictive_score.round(2)

        final_score = (
            df["rule_score"] * 0.38
            + df["anomaly_score"] * 0.22
            + df["predictive_score"] * 0.28
            + df["text_signal_score"] * 0.12
        ).clip(0, 100)
        df["final_risk_score"] = final_score.round(2)
        df["escalation_probability"] = (df["predictive_score"] / 100).round(3)
        df["severity"] = pd.cut(
            df["final_risk_score"],
            bins=[-1, 30, 55, 75, 100],
            labels=["Low", "Moderate", "High", "Critical"]
        ).astype(str)

        recommendations = []
        detailed_reasons = []
        for _, row in df.iterrows():
            reasons = list(row["base_reasons"])
            if row["anomaly_score"] >= 70:
                reasons.append("Statistically anomalous case pattern")
            if row["predictive_score"] >= 75:
                reasons.append("High escalation likelihood from predictive model")
            recommendations.append(recommend_action(row["severity"], reasons))
            detailed_reasons.append(json.dumps(reasons))
        df["recommendation"] = recommendations
        df["reasons"] = detailed_reasons
        return df
