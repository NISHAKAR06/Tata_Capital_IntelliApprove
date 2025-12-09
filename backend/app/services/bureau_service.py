"""Mock bureau integration."""
from __future__ import annotations

import random

from app.schemas.bureau import BureauReport


class BureauService:
    """Return a deterministic mock bureau report."""

    def fetch_report(self, pan: str | None) -> BureauReport:
        seed = sum(ord(ch) for ch in (pan or "TATA0000"))
        random.seed(seed)
        score = random.randint(680, 820)
        utilization = round(random.uniform(0.25, 0.65), 2)
        accounts = random.randint(2, 5)
        return BureauReport(score=score, utilization=utilization, accounts=accounts)
