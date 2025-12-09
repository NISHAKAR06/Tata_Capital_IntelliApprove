"""Utility helpers for EMI math."""
from __future__ import annotations

from typing import Dict, List


def calculate_emi(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    monthly_rate = annual_rate_percent / 12 / 100
    if monthly_rate == 0:
        return round(principal / tenure_months, 2)

    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    return round(emi, 2)


def build_amortization_schedule(
    principal: float, annual_rate_percent: float, tenure_months: int
) -> List[Dict[str, float]]:
    emi = calculate_emi(principal, annual_rate_percent, tenure_months)
    balance = principal
    schedule: List[Dict[str, float]] = []

    if emi == 0:
        return schedule

    monthly_rate = annual_rate_percent / 12 / 100

    for installment in range(1, tenure_months + 1):
        interest = round(balance * monthly_rate, 2)
        principal_component = round(emi - interest, 2)
        balance = max(0.0, round(balance - principal_component, 2))
        schedule.append(
            {
                "month": float(installment),
                "interest": interest,
                "principal": principal_component,
                "balance": balance,
            }
        )
        if balance <= 0:
            break

    return schedule
