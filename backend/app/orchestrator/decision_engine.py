from __future__ import annotations

from typing import Any, Dict, Optional

from ..schemas.underwriting import UnderwritingExplainability, ExplainabilityFactor

BASE_RATE = 11.5
FLOOR_RATE = 9.0


def compute_personalized_rate(
    credit_score: Optional[int],
    loyalty_years: Optional[int],
    auto_debit_enabled: bool,
    utilization_lt_30: bool,
    is_home_loan_customer: bool,
) -> float:
    rate = BASE_RATE

    if credit_score is not None and credit_score >= 780:
        rate -= 1.5
    if loyalty_years is not None and loyalty_years >= 5:
        rate -= 0.5
    if auto_debit_enabled:
        rate -= 0.3
    if utilization_lt_30:
        rate -= 0.3
    if is_home_loan_customer:
        rate -= 0.4

    return round(max(rate, FLOOR_RATE), 2)


def compute_emi(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    r = annual_rate_percent / 12 / 100
    n = tenure_months

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

    return round(emi, 2)


def run_underwriting_rules(
    credit_score: Optional[int],
    loan_amount: float,
    pre_approved_limit: Optional[float],
    monthly_income: Optional[float],
    proposed_emi: Optional[float],
) -> UnderwritingExplainability:
    factors: list[ExplainabilityFactor] = []

    if credit_score is None:
        factors.append(
            ExplainabilityFactor(
                name="credit_score",
                value=None,
                threshold="≥ 700",
                status="fail",
                reason="Credit score missing",
            )
        )
        return UnderwritingExplainability(
            decision="rejected",
            summary="Rejected due to missing credit score.",
            factors=factors,
        )

    if credit_score < 700:
        factors.append(
            ExplainabilityFactor(
                name="credit_score",
                value=str(credit_score),
                threshold="≥ 700",
                status="fail",
                reason="Credit score below minimum threshold.",
            )
        )
        return UnderwritingExplainability(
            decision="rejected",
            summary="Rejected because credit score is below 700.",
            factors=factors,
        )

    factors.append(
        ExplainabilityFactor(
            name="credit_score",
            value=str(credit_score),
            threshold=">= 700",
            status="pass",
            reason="Credit score meets minimum threshold.",
        )
    )

    if pre_approved_limit is not None:
        if loan_amount > 2 * pre_approved_limit:
            factors.append(
                ExplainabilityFactor(
                    name="loan_vs_preapproved",
                    value=str(loan_amount),
                    threshold=f"≤ 2 × {pre_approved_limit}",
                    status="fail",
                    reason="Requested amount exceeds 2× pre-approved limit.",
                )
            )
            return UnderwritingExplainability(
                decision="rejected",
                summary="Rejected because requested amount exceeds 2× pre-approved limit.",
                factors=factors,
            )
        elif loan_amount > pre_approved_limit:
            factors.append(
                ExplainabilityFactor(
                    name="loan_vs_preapproved",
                    value=str(loan_amount),
                    threshold=f"≤ 2 × {pre_approved_limit}",
                    status="conditional",
                    reason="Loan between pre-approved and 2× limit – salary slip required.",
                )
            )
        else:
            factors.append(
                ExplainabilityFactor(
                    name="loan_vs_preapproved",
                    value=str(loan_amount),
                    threshold=f"≤ {pre_approved_limit}",
                    status="pass",
                    reason="Loan amount within pre-approved limit.",
                )
            )
    else:
        factors.append(
            ExplainabilityFactor(
                name="loan_vs_preapproved",
                value=str(loan_amount),
                threshold="pre-approved limit missing",
                status="unknown",
                reason="Pre-approved limit not available.",
            )
        )

    if monthly_income is None or proposed_emi is None or proposed_emi <= 0:
        factors.append(
            ExplainabilityFactor(
                name="dti_ratio",
                value=None,
                threshold="EMI / Salary ≤ 50%",
                status="fail",
                reason="Monthly income or EMI missing.",
            )
        )
        return UnderwritingExplainability(
            decision="rejected",
            summary="Rejected because income or EMI data is missing for DTI calculation.",
            factors=factors,
        )

    dti_ratio = proposed_emi / monthly_income
    dti_percent = round(dti_ratio * 100, 2)

    if dti_ratio <= 0.5:
        factors.append(
            ExplainabilityFactor(
                name="dti_ratio",
                value=f"{dti_percent}%",
                threshold="≤ 50%",
                status="pass",
                reason="EMI within 50% of income.",
            )
        )
        return UnderwritingExplainability(
            decision="approved",
            summary="Approved: credit score is acceptable and EMI is within 50% of income.",
            factors=factors,
        )

    factors.append(
        ExplainabilityFactor(
            name="dti_ratio",
            value=f"{dti_percent}%",
            threshold="≤ 50%",
            status="fail",
            reason="EMI exceeds 50% of income.",
        )
    )
    return UnderwritingExplainability(
        decision="rejected",
        summary="Rejected: EMI exceeds 50% of declared monthly income.",
        factors=factors,
    )
