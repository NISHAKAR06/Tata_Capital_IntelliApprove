"""Underwriting worker using Ollama."""
from __future__ import annotations

from typing import Dict, Any, Optional

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_underwriting_system_prompt


class UnderwritingAgent:
    def __init__(self) -> None:
        settings = get_settings()
        # Prefer Ollama underwriting model when configured
        model_name = settings.ollama_model_underwriting or settings.ollama_model_default
        self._client = OllamaClient(model=model_name)
        self._base_system_prompt = get_underwriting_system_prompt()

    def evaluate_credit_score(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edge Case #1: Loan Rejection (Low Credit Score)
        """
        credit_score = customer_profile.get('credit_score', 750) # Default to good if missing
        
        if credit_score < 700:
            return {
                'decision': 'REJECTED',
                'reason': 'credit_score_below_threshold',
                'credit_score': credit_score,
                'threshold': 700,
                'gap': 700 - credit_score,
                'action': 'provide_credit_improvement_plan'
            }
        return {'decision': 'APPROVED_CREDIT_CHECK'}

    def evaluate_conditional_approval(self, customer_profile: Dict[str, Any], loan_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edge Case #2: Conditional Approval (Salary Slip Required)
        """
        pre_approved = customer_profile.get('pre_approved_limit', 300000)
        requested = loan_request.get('amount', 500000)
        
        if pre_approved < requested <= 2 * pre_approved:
            return {
                'decision': 'CONDITIONAL_APPROVAL',
                'condition': 'salary_slip_required',
                'reason': 'amount_exceeds_pre_approved_limit',
                'required_documents': ['salary_slip_last_3_months'],
                'emi_threshold': 0.5,  # 50% of salary
                'message': 'need_to_verify_current_income'
            }
        elif requested > 2 * pre_approved:
             return {
                'decision': 'REJECTED',
                'reason': 'amount_too_high_vs_preapproved',
             }
        
        return {'decision': 'INSTANT_APPROVAL'}

    def reevaluate_with_salary(self, customer_profile: Dict, loan_request: Dict, salary_data: Dict) -> Dict:
        """
        Re-evaluation after document upload.
        """
        net_salary = salary_data.get('net_monthly_salary', 0)
        requested_emi = loan_request.get('emi', 0)
        
        if net_salary == 0:
             return {'decision': 'MANUAL_REVIEW', 'reason': 'salary_extraction_failed'}

        # Calculate EMI-to-Income ratio
        emi_ratio = (requested_emi / net_salary) * 100
        
        if emi_ratio <= 50:
            return {
                'decision': 'APPROVED',
                'approved_amount': loan_request.get('amount'),
                'interest_rate': 10.5,
                'emi': requested_emi,
                'emi_to_income_ratio': emi_ratio,
                'rationale': f'EMI is {emi_ratio:.1f}% of salary (Well within 50% limit)',
                'approval_type': 'CONDITIONAL_CLEARED'
            }
        else:
            # Suggest lower amount
            max_affordable_emi = net_salary * 0.5
            # Simplified calc
            return {
                'decision': 'PARTIAL_APPROVAL',
                'reason': 'EMI exceeds 50% of salary',
                'max_affordable_emi': max_affordable_emi
            }

    def explain_decision(self, explainability: Dict[str, object]) -> str:
        if not self._client.available:
            summary = explainability.get("summary") if isinstance(explainability, dict) else None
            return summary or "Underwriting completed."
        system_prompt = self._base_system_prompt or "You are an underwriting agent. Explain underwriting result in plain English under 80 words."
        return self._client.generate(system_prompt, str(explainability), max_tokens=200) or "Underwriting completed."
