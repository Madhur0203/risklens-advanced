from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.orm import CaseRecord, FeedbackRecord


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def replace_cases(self, df: pd.DataFrame) -> None:
        self.db.query(CaseRecord).delete()
        self.db.commit()
        objects = []
        for row in df.to_dict(orient="records"):
            objects.append(CaseRecord(**{
                k: v for k, v in row.items()
                if k in CaseRecord.__table__.columns.keys()
            }))
        self.db.bulk_save_objects(objects)
        self.db.commit()

    def append_cases(self, df: pd.DataFrame) -> None:
        objects = []
        for row in df.to_dict(orient="records"):
            objects.append(CaseRecord(**{
                k: v for k, v in row.items()
                if k in CaseRecord.__table__.columns.keys()
            }))
        self.db.bulk_save_objects(objects)
        self.db.commit()

    def get_cases(self, filters: dict[str, Any]) -> list[CaseRecord]:
        query = self.db.query(CaseRecord)
        if severity := filters.get("severity"):
            query = query.filter(CaseRecord.severity == severity)
        if vendor := filters.get("vendor"):
            query = query.filter(CaseRecord.vendor == vendor)
        if port := filters.get("port"):
            query = query.filter(CaseRecord.port == port)
        if carrier := filters.get("carrier"):
            query = query.filter(CaseRecord.carrier == carrier)
        if keyword := filters.get("keyword"):
            query = query.filter(CaseRecord.notes.ilike(f"%{keyword}%"))
        if min_score := filters.get("min_score"):
            query = query.filter(CaseRecord.final_risk_score >= float(min_score))
        return query.order_by(CaseRecord.final_risk_score.desc()).all()

    def get_case(self, case_id: str) -> CaseRecord | None:
        return self.db.query(CaseRecord).filter(CaseRecord.case_id == case_id).first()

    def add_feedback(self, case_id: str, analyst_label: str, analyst_comment: str | None) -> None:
        feedback = FeedbackRecord(case_id=case_id, analyst_label=analyst_label, analyst_comment=analyst_comment or "")
        self.db.add(feedback)
        self.db.commit()

    def dashboard(self) -> dict[str, Any]:
        all_cases = self.db.query(CaseRecord).all()
        if not all_cases:
            return {"kpis": {}, "distribution": [], "trend": [], "top_vendors": [], "top_ports": [], "top_carriers": []}
        rows = []
        for row in all_cases:
            rows.append({
                "case_id": row.case_id,
                "vendor": row.vendor,
                "carrier": row.carrier,
                "port": row.port,
                "severity": row.severity,
                "final_risk_score": row.final_risk_score,
                "escalation_probability": row.escalation_probability,
                "created_at": row.created_at.date().isoformat() if row.created_at else None,
            })
        df = pd.DataFrame(rows)
        kpis = {
            "total_cases": int(len(df)),
            "avg_risk_score": round(float(df["final_risk_score"].mean()), 2),
            "critical_cases": int((df["severity"] == "Critical").sum()),
            "high_cases": int((df["severity"] == "High").sum()),
            "avg_escalation_probability": round(float(df["escalation_probability"].mean() * 100), 2),
        }
        distribution = (
            df.groupby("severity").size().reset_index(name="count").to_dict(orient="records")
        )
        trend = (
            df.groupby("created_at")["final_risk_score"].mean().reset_index(name="avg_risk_score").to_dict(orient="records")
        )
        top_vendors = (
            df.groupby("vendor")["final_risk_score"].mean().sort_values(ascending=False).head(8).reset_index(name="avg_risk_score").to_dict(orient="records")
        )
        top_ports = (
            df.groupby("port")["final_risk_score"].mean().sort_values(ascending=False).reset_index(name="avg_risk_score").to_dict(orient="records")
        )
        top_carriers = (
            df.groupby("carrier")["final_risk_score"].mean().sort_values(ascending=False).reset_index(name="avg_risk_score").to_dict(orient="records")
        )
        return {
            "kpis": kpis,
            "distribution": distribution,
            "trend": trend,
            "top_vendors": top_vendors,
            "top_ports": top_ports,
            "top_carriers": top_carriers,
        }

    def get_feature_feedback_summary(self) -> dict[str, int]:
        rows = self.db.query(FeedbackRecord.analyst_label, func.count(FeedbackRecord.id)).group_by(FeedbackRecord.analyst_label).all()
        return {label: count for label, count in rows}
