"""Underwriting worker encapsulating Tata Capital credit rules.

This agent is responsible for turning raw customer + bureau data into
discrete underwriting decisions that map to the main product flows
described in the edge‑case test matrix, for example:

- ``INSTANT_APPROVE`` – strong profile, low DTI
- ``NEEDS_SALARY_VERIFICATION`` – mid‑tier score / high DTI but salvageable
- ``MANUAL_REVIEW`` – multiple risk factors, needs human underwriter
- ``REJECT`` – clearly outside risk appetite
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_underwriting_system_prompt
from app.orchestrator.decision_engine import run_underwriting_rules
from app.utils.loan_math import debt_to_income


class UnderwritingAgent:
    def __init__(self) -> None:
        settings = get_settings()
        # Prefer dedicated underwriting model when configured
        model_name = settings.ollama_model_underwriting or settings.ollama_model_default
        self._client = OllamaClient(model=model_name)
        self._base_system_prompt = get_underwriting_system_prompt()

    # ------------------------
    #  Core rule entry points
    # ------------------------

    def evaluate_credit_score(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Pure score‑based gate used as the first filter.

        Maps directly to scenarios where a very low score results in
        immediate rejection with an improvement plan.
        """

        credit_score = int(customer_profile.get("credit_score") or 0)

        if credit_score <= 0:
            return {
                "decision": "REJECT",
                "reason": "credit_score_missing",
                "credit_score": None,
                "threshold": 700,
                "action": "request_bureau_refresh",
            }

        if credit_score < 700:
            # Align with scenarios: straight rejection below 700
            return {
                "decision": "REJECT",
                "reason": "credit_score_below_threshold",
                "credit_score": credit_score,
                "threshold": 700,
                "gap": 700 - credit_score,
                "action": "provide_credit_improvement_plan",
            }

        # 700–749 → mid‑tier, continue but typically needs salary verification
        if 700 <= credit_score < 750:
            return {
                "decision": "MID_TIER_SCORE",
                "credit_score": credit_score,
            }

        # ≥ 750 → low‑risk profile
        return {
            "decision": "GOOD_SCORE",
            "credit_score": credit_score,
        }

    def evaluate_conditional_approval(self, customer_profile: Dict[str, Any], loan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Combine pre‑approved limit, income, EMI and bureau flags.

        This method is the main mapping between your documented
        scenarios (1–4) and internal decisions:

        - INSTANT_APPROVE (Scenario 1, 5)
        - NEEDS_SALARY_VERIFICATION (Scenario 2)
        - MANUAL_REVIEW (Scenario 3)
        - REJECT (Scenario 4)
        """

        pre_approved = float(customer_profile.get("pre_approved_limit") or 0.0)
        requested = float(loan_request.get("amount") or 0.0)
        monthly_income = float(customer_profile.get("monthly_income") or 0.0)

        # Existing obligations from CRM / bureau snapshot if present
        existing_emi = 0.0
        for loan in customer_profile.get("existing_loans", []) or []:
            try:
                existing_emi += float(loan.get("emi") or 0.0)
            except Exception:
                continue

        proposed_emi = float(loan_request.get("emi") or 0.0)
        total_emi = existing_emi + proposed_emi

        dti_ratio = debt_to_income(total_emi, monthly_income)  # 0–1 «emi / income»
        dti_percent = round(dti_ratio * 100, 2)

        # Additional risk signals when available
        bureau = (customer_profile.get("bureau_report") or {}) if isinstance(customer_profile.get("bureau_report"), dict) else {}
        defaults = int(bureau.get("payment_defaults") or bureau.get("defaults") or 0)
        enquiries_6m = int(bureau.get("enquiries_last_6_months") or 0)

        # Map core numeric rules into an explainability object
        uw_expl = run_underwriting_rules(
            credit_score=int(customer_profile.get("credit_score") or 0),
            loan_amount=requested,
            pre_approved_limit=pre_approved or None,
            monthly_income=monthly_income or None,
            proposed_emi=proposed_emi or None,
        )

        base_decision = (uw_expl.decision or "rejected").lower()

        # Hard stops first – very high DTI or many recent defaults
        if dti_ratio > 1.0 or defaults >= 2:
            return {
                "decision": "MANUAL_REVIEW",
                "reason": "multiple_risk_factors_high_dti_or_defaults",
                "dti_ratio": dti_percent,
                "defaults": defaults,
                "enquiries_6m": enquiries_6m,
            }

        # Credit score / amount are acceptable but EMI band is moderate
        if base_decision == "approved":
            if dti_ratio <= 0.5:
                return {
                    "decision": "INSTANT_APPROVE",
                    "dti_ratio": dti_percent,
                    "existing_emi": existing_emi,
                    "proposed_emi": proposed_emi,
                }

            if 0.5 < dti_ratio <= 1.0:
                return {
                    "decision": "NEEDS_SALARY_VERIFICATION",
                    "reason": "emi_to_income_between_50_and_100",
                    "dti_ratio": dti_percent,
                    "existing_emi": existing_emi,
                    "proposed_emi": proposed_emi,
                    "required_documents": ["salary_slip_last_3_months"],
                }

        # Any conditional / borderline outcome that is not a hard reject
        if base_decision in {"conditional", "partial_approval"} or (defaults == 1 or enquiries_6m >= 5):
            return {
                "decision": "MANUAL_REVIEW",
                "reason": "borderline_profile_needs_human_underwriter",
                "dti_ratio": dti_percent,
                "defaults": defaults,
                "enquiries_6m": enquiries_6m,
            }

        # Fallback – keep semantic REJECT for caller
        return {
            "decision": "REJECT",
            "reason": uw_expl.summary or "profile_outside_risk_appetite",
            "dti_ratio": dti_percent,
            "defaults": defaults,
            "enquiries_6m": enquiries_6m,
        }

    def reevaluate_with_salary(self, customer_profile: Dict[str, Any], loan_request: Dict[str, Any], salary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Re-evaluate after salary slip / income verification.

        Implements Scenario 2 / 6C salary‑verification branch:
        if verified EMI‑to‑income ≤ 50% → APPROVED, otherwise PARTIAL_APPROVAL
        with a suggested max affordable EMI.
        """

        net_salary = float(salary_data.get("net_monthly_salary") or 0.0)
        requested_emi = float(loan_request.get("emi") or 0.0)

        if net_salary <= 0:
            return {"decision": "MANUAL_REVIEW", "reason": "salary_extraction_failed"}

        emi_ratio = (requested_emi / net_salary) * 100 if requested_emi > 0 else 0.0

        if emi_ratio <= 50.0:
            return {
                "decision": "APPROVED",
                "approved_amount": loan_request.get("amount"),
                "interest_rate": 10.5,
                "emi": requested_emi,
                "emi_to_income_ratio": emi_ratio,
                "rationale": f"EMI is {emi_ratio:.1f}% of salary (within 50% limit)",
                "approval_type": "CONDITIONAL_CLEARED",
            }

        max_affordable_emi = net_salary * 0.5
        return {
            "decision": "PARTIAL_APPROVAL",
            "reason": "emi_exceeds_50_percent_of_salary",
            "max_affordable_emi": max_affordable_emi,
            "emi_to_income_ratio": emi_ratio,
        }

    # ------------------------
    #  Explainability helper
    # ------------------------

    def explain_decision(self, explainability: Dict[str, object]) -> str:
        """Return a short, customer‑friendly explanation string."""

        if not self._client.available:
            summary = explainability.get("summary") if isinstance(explainability, dict) else None
            return summary or "Underwriting completed."

        system_prompt = (
            self._base_system_prompt
            or "You are an underwriting agent. Explain underwriting result in plain English under 80 words."
        )
        return self._client.generate(system_prompt, str(explainability), max_tokens=200) or "Underwriting completed."
