from __future__ import annotations

import io
import json
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import FeedbackIn
from app.core.database import get_db
from app.models.orm import CaseRecord
from app.services.data_generator import generate_cases
from app.services.repository import Repository
from app.services.risk_engine import RiskEngine

router = APIRouter()
engine_state = RiskEngine()


def _case_to_dict(case: CaseRecord) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "vendor": case.vendor,
        "carrier": case.carrier,
        "port": case.port,
        "route": case.route,
        "filing_status": case.filing_status,
        "notes": case.notes,
        "amount": case.amount,
        "quantity": case.quantity,
        "delay_days": case.delay_days,
        "document_completeness": case.document_completeness,
        "vendor_incident_rate": case.vendor_incident_rate,
        "route_rarity": case.route_rarity,
        "cost_spike": case.cost_spike,
        "exception_count": case.exception_count,
        "text_signal_score": case.text_signal_score,
        "rule_score": case.rule_score,
        "anomaly_score": case.anomaly_score,
        "predictive_score": case.predictive_score,
        "final_risk_score": case.final_risk_score,
        "severity": case.severity,
        "escalation_probability": case.escalation_probability,
        "recommendation": case.recommendation,
        "reasons": json.loads(case.reasons or "[]"),
    }


def _read_file(file: UploadFile) -> pd.DataFrame:
    suffix = file.filename.lower()
    content = file.file.read()
    if suffix.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    if suffix.endswith(".xlsx") or suffix.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    raise HTTPException(status_code=400, detail=f"Unsupported file type for {file.filename}")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/bootstrap")
def bootstrap(db: Session = Depends(get_db)):
    raw = generate_cases(1200)
    scored = engine_state.train(raw)
    repo = Repository(db)
    repo.replace_cases(scored)
    return {"message": "Bootstrap dataset generated and model trained.", "rows": len(scored)}


@router.post("/upload")
async def upload(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    dfs = []
    for file in files:
        df = _read_file(file)
        dfs.append(df)
    merged = pd.concat(dfs, ignore_index=True)

    required_cols = {
        "case_id", "vendor", "carrier", "port", "route", "filing_status", "notes",
        "amount", "quantity", "delay_days", "document_completeness", "vendor_incident_rate",
        "route_rarity", "cost_spike", "exception_count"
    }
    missing = required_cols - set(merged.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {sorted(missing)}")
    if "label_escalated" not in merged.columns:
        merged["label_escalated"] = 0

    if not engine_state.artifacts:
        engine_state.train(generate_cases(1000))
    scored = engine_state.score_new(merged)
    repo = Repository(db)
    repo.replace_cases(scored)
    return {"message": "Files ingested and scored.", "rows": len(scored)}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return Repository(db).dashboard()


@router.get("/cases")
def cases(
    severity: str | None = None,
    vendor: str | None = None,
    port: str | None = None,
    carrier: str | None = None,
    keyword: str | None = None,
    min_score: float | None = None,
    db: Session = Depends(get_db)
):
    repo = Repository(db)
    rows = repo.get_cases({
        "severity": severity,
        "vendor": vendor,
        "port": port,
        "carrier": carrier,
        "keyword": keyword,
        "min_score": min_score,
    })
    return {
        "items": [_case_to_dict(row) for row in rows],
        "filters": {
            "severities": ["Low", "Moderate", "High", "Critical"],
            "vendors": sorted({row.vendor for row in rows}),
            "ports": sorted({row.port for row in rows}),
            "carriers": sorted({row.carrier for row in rows}),
        },
        "feature_importances": engine_state.artifacts.feature_importances if engine_state.artifacts else {}
    }


@router.get("/cases/{case_id}")
def case_detail(case_id: str, db: Session = Depends(get_db)):
    row = Repository(db).get_case(case_id)
    if not row:
        raise HTTPException(status_code=404, detail="Case not found.")
    return _case_to_dict(row)


@router.post("/feedback")
def feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    Repository(db).add_feedback(payload.case_id, payload.analyst_label, payload.analyst_comment)
    return {"message": "Feedback captured."}


@router.post("/retrain")
def retrain(db: Session = Depends(get_db)):
    repo = Repository(db)
    existing = repo.get_cases({})
    if not existing:
        raise HTTPException(status_code=400, detail="No cases available for retraining.")
    rows = []
    feedback_summary = repo.get_feature_feedback_summary()
    weight_boost = 1 if feedback_summary.get("true_positive", 0) >= feedback_summary.get("false_positive", 0) else 0
    for row in existing:
        rows.append({
            "case_id": row.case_id,
            "vendor": row.vendor,
            "carrier": row.carrier,
            "port": row.port,
            "route": row.route,
            "filing_status": row.filing_status,
            "notes": row.notes,
            "amount": row.amount,
            "quantity": row.quantity,
            "delay_days": row.delay_days,
            "document_completeness": row.document_completeness,
            "vendor_incident_rate": row.vendor_incident_rate + (0.03 * weight_boost),
            "route_rarity": row.route_rarity,
            "cost_spike": row.cost_spike,
            "exception_count": row.exception_count,
            "label_escalated": 1 if row.severity in {"High", "Critical"} else 0,
        })
    df = pd.DataFrame(rows)
    scored = engine_state.train(df)
    repo.replace_cases(scored)
    return {"message": "Model retrained on current case base.", "rows": len(scored)}
