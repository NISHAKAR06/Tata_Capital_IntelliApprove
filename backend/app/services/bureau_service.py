"""Bureau integration backed by the local Credit Bureau mock server."""
from __future__ import annotations

from typing import Optional

import httpx

from app.config.settings import get_settings
from app.schemas.bureau import BureauReport


class BureauService:
    """Fetch a bureau snapshot from the credit_bureau_server mock.

    The mock server is exposed by backend/mock_servers/credit_bureau_server.py
    and started on http://localhost:8002 by scripts.run_mock_servers.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.bureau_api_base.rstrip("/")
        self._timeout = settings.request_timeout_seconds

    def _safe_get(self, path: str) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.get(url, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def fetch_report(self, pan: str | None) -> BureauReport:
        """Return a BureauReport using real mock bureau data when available."""

        if not pan:
            # Fallback demo behaviour when PAN is missing
            return BureauReport(score=750, utilization=0.35, accounts=3)

        # 1) Get core credit score
        score = 750
        body = self._safe_get(f"/credit-score/{pan}")
        if body and body.get("status") == "success" and body.get("data"):
            data = body["data"]
            score = int(data.get("credit_score", score))

        # 2) Optionally enrich with account count from debt obligations
        utilization = 0.35
        accounts = 3
        debt_body = self._safe_get(f"/debt-obligations/{pan}")
        if debt_body and debt_body.get("status") == "success" and debt_body.get("data"):
            debt_data = debt_body["data"]
            debt_summary = debt_data.get("debt_summary") or {}
            accounts = int(debt_summary.get("existing_loans_count", accounts))

        return BureauReport(score=score, utilization=utilization, accounts=accounts)
