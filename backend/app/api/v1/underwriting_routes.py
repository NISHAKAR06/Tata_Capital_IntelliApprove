"""Underwriting evaluation endpoints.

Expose simple REST APIs for underwriting decisions so that
/api/underwriting/evaluate and /api/underwriting/re-evaluate from the
edge-case test matrix are backed by the same rules used in the chat
orchestrator.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_underwriting_agent
from app.workers.underwriting_agent import UnderwritingAgent

router = APIRouter(prefix="/underwriting", tags=["Underwriting"])


class UnderwritingEvaluateRequest(BaseModel):
    application_id: Optional[str] = None
    credit_score: int
    loan_amount: float
    pre_approved_limit: Optional[float] = None
    monthly_income: Optional[float] = None
    proposed_emi: Optional[float] = None
    defaults: Optional[int] = 0
    enquiries_6m: Optional[int] = 0


@router.post("/evaluate")
def evaluate(
    payload: UnderwritingEvaluateRequest,
    agent: UnderwritingAgent = Depends(get_underwriting_agent),
) -> Dict[str, Any]:
    """Run core underwriting rules and return a high-level decision.

    This maps the request into the existing UnderwritingAgent inputs so
    the same INSTANT_APPROVE / NEEDS_SALARY_VERIFICATION /
    MANUAL_REVIEW / REJECT decisions are returned.
    """

    customer_profile: Dict[str, Any] = {
        "credit_score": payload.credit_score,
        "pre_approved_limit": payload.pre_approved_limit,
        "monthly_income": payload.monthly_income,
        "bureau_report": {
            "payment_defaults": payload.defaults,
            "enquiries_last_6_months": payload.enquiries_6m,
        },
    }

    loan_req: Dict[str, Any] = {
        "amount": payload.loan_amount,
        "emi": payload.proposed_emi or 0.0,
    }

    result = agent.evaluate_conditional_approval(customer_profile, loan_req)
    # Attach application_id for traceability if provided
    if payload.application_id:
        result.setdefault("application_id", payload.application_id)
    return result


class UnderwritingReEvaluateRequest(BaseModel):
    application_id: Optional[str] = None
    salary_verified: bool = True
    verification_status: str = "PASSED"
    net_monthly_salary: float
    loan_amount: float
    proposed_emi: float


@router.post("/re-evaluate")
def re_evaluate(
    payload: UnderwritingReEvaluateRequest,
    agent: UnderwritingAgent = Depends(get_underwriting_agent),
) -> Dict[str, Any]:
    """Re-run underwriting after salary / income verification.

    Wraps the same salary-slip logic used by the orchestrator so the
    REST API mirrors the documented /underwriting/re-evaluate behavior.
    """

    salary_data = {"net_monthly_salary": payload.net_monthly_salary}
    loan_req = {"amount": payload.loan_amount, "emi": payload.proposed_emi}

    result = agent.reevaluate_with_salary({}, loan_req, salary_data)
    if payload.application_id:
        result.setdefault("application_id", payload.application_id)
    return result
