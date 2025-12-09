"""Ecosystem offer APIs."""
from __future__ import annotations

from typing import List


class OffermartService:
    def list_partner_offers(self, customer_segment: str | None = None) -> List[dict]:
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
