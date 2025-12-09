"""Higher-level financial utilities built on top of EMI helpers."""
from __future__ import annotations

from typing import Optional

from .emi_utils import calculate_emi


def loan_to_value(loan_amount: float, asset_value: float) -> float:
    if loan_amount <= 0 or asset_value <= 0:
        return 0.0
    return round(min(loan_amount / asset_value, 1.0), 2)


def debt_to_income(monthly_emi: float, monthly_income: Optional[float]) -> float:
    if monthly_income is None or monthly_income <= 0:
        return 1.0
    return round(min(monthly_emi / monthly_income, 2.0), 2)


def refresh_offer(
    principal: float,
    base_rate: float,
    credit_score: Optional[int],
    tenure_months: int,
) -> dict[str, float]:
    rate = base_rate
    if credit_score and credit_score >= 780:
        rate = max(base_rate - 1.2, 8.5)
    emi = calculate_emi(principal, rate, tenure_months)
    return {"rate": rate, "emi": emi}
