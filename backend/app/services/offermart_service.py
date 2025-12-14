"""OfferMart integration backed by the local Offer Mart mock server."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.config.settings import get_settings


class OffermartService:
    """Call the Offer Mart mock to get eligibility and concrete offers."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.offermart_api_base.rstrip("/")
        self._timeout = settings.request_timeout_seconds

    def _post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_best_offer(
        self,
        *,
        pan: str,
        monthly_income: float,
        credit_score: int,
        existing_debt: float,
        desired_amount: float,
        desired_tenure: int,
    ) -> Optional[Dict[str, Any]]:
        """Return a single best offer dict from Offer Mart mock, or None."""

        request = {
            "pan_number": pan,
            "monthly_income": monthly_income,
            "credit_score": credit_score,
            "existing_debt": existing_debt,
            "desired_amount": desired_amount,
            "desired_tenure": desired_tenure,
        }

        body = self._post("/get-best-offer", request)
        if not body or body.get("status") != "success":
            return None

        return body.get("data") or body.get("best_offer")

    def list_partner_offers(self, customer_segment: str | None = None) -> List[dict]:
        """Backwards-compatible stub for ecosystem offers (unchanged API)."""

        offers = [
            {
                "partner": "Tata Croma",
                "description": "5% cashback on electronics",
                "cta": "https://croma.com/cashback",
            },
            {
                "partner": "Tata Neu",
                "description": "2,000 NeuCoins on first EMI payment",
                "cta": "https://tataneu.com/rewards",
            },
        ]
        return offers if not customer_segment else offers[:1]
