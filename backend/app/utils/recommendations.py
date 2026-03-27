from __future__ import annotations


def recommend_action(severity: str, reasons: list[str]) -> str:
    joined = " ".join(reasons).lower()
    if severity == "Critical":
        return "Hold release, escalate to compliance manager, and perform same-day document review."
    if "penalty" in joined or "hold" in joined:
        return "Open a priority compliance review and verify supporting customs documentation."
    if "mismatch" in joined or "inconsistent" in joined:
        return "Request invoice / quantity validation and compare with filing records."
    if "document" in joined:
        return "Request missing documents before final approval."
    if severity == "High":
        return "Prioritize analyst review within 24 hours and monitor vendor history."
    return "Monitor case and keep in watchlist; no immediate escalation required."
