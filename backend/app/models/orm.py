from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from app.core.database import Base


class CaseRecord(Base):
    __tablename__ = "case_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    vendor = Column(String, index=True)
    carrier = Column(String, index=True)
    port = Column(String, index=True)
    route = Column(String)
    filing_status = Column(String)
    notes = Column(Text)
    amount = Column(Float)
    quantity = Column(Float)
    delay_days = Column(Float)
    document_completeness = Column(Float)
    vendor_incident_rate = Column(Float)
    route_rarity = Column(Float)
    cost_spike = Column(Float)
    exception_count = Column(Float)
    text_signal_score = Column(Float)
    rule_score = Column(Float)
    anomaly_score = Column(Float)
    predictive_score = Column(Float)
    final_risk_score = Column(Float)
    severity = Column(String, index=True)
    escalation_probability = Column(Float)
    recommendation = Column(String)
    reasons = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, index=True)
    analyst_label = Column(String)
    analyst_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
