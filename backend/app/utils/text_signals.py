from __future__ import annotations

import re
from typing import Dict, List, Tuple

RISK_PATTERNS = {
    "delay": [r"delay", r"late filing", r"held at port", r"missed cutoff"],
    "documents": [r"missing doc", r"missing document", r"incomplete", r"resubmission"],
    "penalty": [r"penalty", r"fine", r"customs hold", r"violation"],
    "mismatch": [r"mismatch", r"inconsistent", r"incorrect qty", r"wrong hts"],
    "urgency": [r"urgent review", r"escalate", r"priority", r"manual review"],
}

WEIGHTS = {
    "delay": 8,
    "documents": 10,
    "penalty": 15,
    "mismatch": 12,
    "urgency": 7,
}


def extract_text_signals(text: str | None) -> Tuple[float, Dict[str, int], List[str]]:
    if not text:
        return 0.0, {}, []
    lowered = text.lower()
    bucket_counts: Dict[str, int] = {}
    evidence: List[str] = []
    total = 0.0
    for bucket, patterns in RISK_PATTERNS.items():
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, lowered)
            count += len(matches)
        if count:
            bucket_counts[bucket] = count
            total += min(WEIGHTS[bucket] * count, WEIGHTS[bucket] * 2)
            evidence.append(f"{bucket}: {count} signal(s)")
    return min(total, 35.0), bucket_counts, evidence
