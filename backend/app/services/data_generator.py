from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.core.settings import settings

VENDORS = [
    "Apex Global Metals", "Ramratna Components", "RRK Trade Lines", "Nova Wire Supply",
    "Blue Harbor Imports", "West Port Industrial", "Delta Alloy Works", "Vertex Cable Systems"
]
CARRIERS = ["MSC", "Maersk", "CMA CGM", "Hapag-Lloyd", "ONE", "Evergreen"]
PORTS = ["Newark", "Houston", "Savannah", "Los Angeles", "Norfolk", "Charleston"]
ROUTES = ["IN-US", "VN-US", "CN-US", "TR-US", "AE-US", "MX-US"]
NOTE_FRAGMENTS = [
    "Documents complete and verified.",
    "Missing documents caused resubmission.",
    "Urgent review requested after customs hold.",
    "Late filing observed and invoice mismatch under review.",
    "Vendor history clean; only minor delay noted.",
    "Potential penalty risk due to incomplete HS information.",
    "Manual review requested after unusual route change.",
    "Corrected filing submitted after quantity inconsistency.",
]


def generate_cases(n: int = 1200) -> pd.DataFrame:
    random.seed(settings.random_seed)
    np.random.seed(settings.random_seed)
    rows = []
    start = datetime.utcnow() - timedelta(days=180)
    for i in range(n):
        vendor = random.choice(VENDORS)
        carrier = random.choice(CARRIERS)
        port = random.choice(PORTS)
        route = random.choice(ROUTES)
        date = start + timedelta(days=random.randint(0, 180))
        amount = float(np.random.lognormal(mean=9.4, sigma=0.45))
        quantity = float(max(1, np.random.normal(280, 70)))
        delay_days = max(0, round(np.random.normal(1.5, 2.1), 1))
        doc_complete = max(45, min(100, round(np.random.normal(86, 10), 1)))
        incident_rate = round(max(0, min(1, np.random.beta(1.5, 5))), 3)
        route_rarity = round(max(0, min(1, np.random.beta(1.4, 4))), 3)
        cost_spike = round(max(-0.25, min(1.2, np.random.normal(0.1, 0.18))), 3)
        exception_count = int(max(0, np.random.poisson(1.2)))
        filing_status = "On Time"
        if delay_days >= 2:
            filing_status = "Late"
        if delay_days >= 5:
            filing_status = "Critical Delay"
        notes = random.choice(NOTE_FRAGMENTS)

        latent = (
            (delay_days * 4.5)
            + ((100 - doc_complete) * 0.55)
            + (incident_rate * 28)
            + (route_rarity * 16)
            + (max(cost_spike, 0) * 20)
            + (exception_count * 4.5)
        )
        if "missing" in notes.lower():
            latent += 8
        if "penalty" in notes.lower():
            latent += 12
        if "hold" in notes.lower():
            latent += 10
        escalation_probability = 1 / (1 + np.exp(-(latent - 35) / 9))
        rows.append(
            {
                "case_id": f"RL-{i+1:05d}",
                "date": date.date().isoformat(),
                "vendor": vendor,
                "carrier": carrier,
                "port": port,
                "route": route,
                "filing_status": filing_status,
                "notes": notes,
                "amount": round(amount, 2),
                "quantity": round(quantity, 2),
                "delay_days": delay_days,
                "document_completeness": doc_complete,
                "vendor_incident_rate": incident_rate,
                "route_rarity": route_rarity,
                "cost_spike": cost_spike,
                "exception_count": exception_count,
                "label_escalated": int(escalation_probability > 0.5),
            }
        )
    return pd.DataFrame(rows)
