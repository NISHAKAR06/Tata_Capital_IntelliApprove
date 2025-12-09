"""Pricing engine encapsulating business rules."""
from __future__ import annotations

from typing import Dict, Optional

from app.orchestrator.decision_engine import compute_personalized_rate
from app.utils.emi_utils import calculate_emi


class PricingEngine:
    def price_offer(
        self,
        *,
        principal: float,
        tenure_months: int,
        credit_score: Optional[int],
        loyalty_years: Optional[int],
        auto_debit_enabled: bool,
        utilization_lt_30: bool,
        is_home_loan_customer: bool,
    ) -> Dict[str, float]:
        rate = compute_personalized_rate(
            credit_score=credit_score,
            loyalty_years=loyalty_years,
            auto_debit_enabled=auto_debit_enabled,
            utilization_lt_30=utilization_lt_30,
            is_home_loan_customer=is_home_loan_customer,
        )
        emi = calculate_emi(principal, rate, tenure_months)
        return {"rate": rate, "emi": emi}
