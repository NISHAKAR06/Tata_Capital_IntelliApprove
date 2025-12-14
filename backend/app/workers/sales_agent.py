"""Sales stage agent powered by Ollama."""
from __future__ import annotations

from typing import Dict, Any, Optional, List
import json

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_sales_system_prompt
from app.workers.pricing_engine import PricingEngine


class SalesAgent:
    def __init__(self) -> None:
        settings = get_settings()
        # Use per-agent Ollama model
        model_name = settings.ollama_model_sales or settings.ollama_model_default
        self._client = OllamaClient(model=model_name)
        self._base_system_prompt = get_sales_system_prompt()
        self._pricing_engine = PricingEngine()
        self.persuasion_techniques = {
            "active_listening": "I understand your situation.",
            "value_proposition": "This offers great value.",
            "objection_handling": "Let's look at the numbers.",
            "urgency_creation": "This offer is valid for a limited time.",
            "social_proof": "Many customers choose this option.",
            "personalization": "Based on your profile..."
        }

    def craft_pitch(self, context: Dict[str, Any], user_message: str = "", mode: str = "needs_discovery", concern_type: Optional[str] = None, modification: Optional[Dict] = None) -> str:
        """Generate a sales pitch or response based on the mode and context.

        Modes: "needs_discovery", "information_only", "objection_handling", "renegotiation", "closing".
        If the LLM client is not available, we fall back to a rule-based response
        so that the chatbot still behaves intelligently instead of repeating the
        same generic message.
        """
        if not self._client.available:
            return self._rule_based_pitch(context, user_message, mode, concern_type, modification)

        # Construct the prompt based on the mode
        language_instruction = "Use Hindi-English (Hinglish) mix if the user seems comfortable, or standard English."
        if context.get('language') == 'en':
            language_instruction = "Use strictly standard English as requested by the user."
        elif context.get('language') == 'hi':
             language_instruction = "Use Hindi or Hinglish as requested."

        base_prompt = self._base_system_prompt or (
            "You are 'IntelliApprove', an advanced AI loan agent for Tata Capital. "
            "Your goal is to assist customers with personal loans, explain offers, and guide them through the application process. "
            "You must generate your own natural, human-like responses based on the context. "
            "Do not use pre-written or robotic templates. Be helpful, empathetic, and professional."
        )

        system_instruction = f"{base_prompt}\n{language_instruction}\n"

        specific_instructions = ""
        
        if mode == "needs_discovery":
            specific_instructions = (
                "The customer is new or showing interest. "
                "Engage them, ask about their needs (amount, tenure) if not known, or present the offer if available in context. "
                "Highlight benefits."
            )
        elif mode == "information_only":
            specific_instructions = (
                "The customer has questions. Answer them clearly and concisely. "
                "Do not push too hard, but gently guide them back to the application."
            )
        elif mode == "objection_handling":
            specific_instructions = (
                f"The customer has raised an objection: {concern_type}. "
                "Use empathy first ('I understand...'). "
                "Then use data to reassure them. "
                "If affordability is the concern, break down the EMI vs Income. "
                "If rate is the concern, explain the value/market standards."
            )
            if concern_type == "affordability_anxiety":
                 # Inject the affordability calculator logic into the prompt context
                 pass 

        elif mode == "renegotiation":
            specific_instructions = (
                f"The customer wants to modify terms: {modification}. "
                "Check if the modification is feasible (you can assume reasonable requests are okay for this demo). "
                "Offer alternatives if needed (e.g., longer tenure for lower EMI)."
            )
        
        prompt = (
            f"{system_instruction}\n"
            f"MODE: {mode}\n"
            f"CONTEXT DATA: {json.dumps(context, default=str)}\n"
            f"INSTRUCTIONS: {specific_instructions}\n"
            "Keep response under 100 words. Be persuasive but ethical."
        )

        response = self._client.generate(prompt, f"USER SAYS: {user_message}", max_tokens=300)
        if not response:
            # LLM failed or returned empty; fall back to rule-based pitch so
            # conversation stays contextual and does not repeat a generic line.
            return self._rule_based_pitch(context, user_message, mode, concern_type, modification)

        return response

    def handle_affordability_objection(self, customer_profile: Dict, loan_terms: Dict) -> Dict:
        """
        Calculates data for the affordability objection handling (Edge Case logic).
        """
        # Mock logic for the demo
        amount = loan_terms.get("amount", 500000)
        emi = loan_terms.get("emi", 15921)
        income = customer_profile.get("monthly_income", 80000)
        
        # Calculate alternatives
        alt_tenure = 48
        # Simple interest approx for demo
        rate = 0.105
        r = rate / 12
        alt_emi = (amount * r * ((1+r)**alt_tenure)) / (((1+r)**alt_tenure) - 1)
        
        return {
            "breakdown": {
                "income": income,
                "current_emi": 45000, # Mock
                "new_emi": emi,
                "total_emi": 45000 + emi,
                "remaining": income - (45000 + emi)
            },
            "alternatives": [
                {
                    "option": "Longer Tenure",
                    "tenure": 48,
                    "new_emi": int(alt_emi),
                    "savings_per_month": int(emi - alt_emi),
                    "message": f"Reduce EMI by ₹{int(emi - alt_emi)}/month"
                }
            ]
        }

    def _rule_based_pitch(
        self,
        context: Dict[str, Any],
        user_message: str,
        mode: str,
        concern_type: Optional[str] = None,
        modification: Optional[Dict] = None,
    ) -> str:
        """Simple non-LLM fallback so chat is still contextual.

        Uses keywords and basic amount extraction to avoid repeating one
        static line when Ollama is not available.
        """
        text = (user_message or "").lower()

        # Try to infer requested amount and tenure from message or context
        import re

        amount = None
        tenure = None

        # First big number (>= 4 digits) as amount, if present
        match_amount = re.search(r"(\d{4,})", text)
        if match_amount:
            try:
                amount = int(match_amount.group(1))
            except ValueError:
                amount = None

        loan_req = context.get("loan_request") or {}
        amount = amount or loan_req.get("requested_amount")

        # Tenure extraction: look for patterns like "24 months" or small numbers
        match_tenure = re.search(r"(\d{1,3})\s*(months|month|mon)\b", text)
        if match_tenure:
            try:
                tenure = int(match_tenure.group(1))
            except ValueError:
                tenure = None

        if tenure is None:
            tenure = loan_req.get("requested_tenure")

        purpose = (loan_req.get("purpose") or "loan").lower()
        if any(word in text for word in ["car", "bike", "vehicle"]):
            purpose = "vehicle loan"

        if mode == "information_only":
            return (
                "I can walk you through our personal loan details, including interest "
                "rates, eligibility and EMIs. Tell me what you’d like to know more about – "
                "rate, EMI, documents, or approval time."
            )

        if mode == "objection_handling":
            base = "I understand your concern. "
            if concern_type == "affordability_anxiety":
                return (
                    base
                    + "We usually keep EMIs within a comfortable share of your income. "
                    + "If you tell me your monthly income, I can suggest a safer amount or tenure."
                )
            return base + "Tell me what worries you most – rate, EMI, or documents – and I’ll address it step by step."

        if mode == "renegotiation":
            return (
                "We can try adjusting the tenure or amount to make the EMI more comfortable. "
                "For example, a longer tenure reduces the monthly EMI but increases total interest. "
                "Tell me whether you prefer lower EMI or faster closure."
            )

        # Default: needs_discovery / generic
        if amount and tenure:
            # Use pricing engine to give an approximate EMI so the user
            # immediately sees a concrete offer instead of being asked again.
            try:
                pricing = self._pricing_engine.price_offer(
                    principal=float(amount),
                    tenure_months=int(tenure),
                    credit_score=None,
                    loyalty_years=None,
                    auto_debit_enabled=False,
                    utilization_lt_30=True,
                    is_home_loan_customer=False,
                )
                rate = pricing.get("rate")
                emi = pricing.get("emi")
                rate_str = f"{rate:.2f}%" if isinstance(rate, (int, float)) else "our standard rate"
                emi_str = f"₹{int(round(emi))}" if isinstance(emi, (int, float)) else "an affordable monthly EMI"
                return (
                    f"For a {purpose} of about ₹{amount} over {tenure} months, "
                    f"your estimated EMI would be around {emi_str} at an approximate rate of {rate_str} per annum. "
                    "This is an indicative figure – final terms depend on verification and underwriting. "
                    "Shall I proceed with these details?"
                )
            except Exception:
                # If pricing engine fails for any reason, fall back to asking tenure/purpose.
                pass

        if amount and not tenure:
            return (
                f"Got it, you’re looking for a loan of around ₹{amount}. "
                "Next, tell me the tenure you prefer in months (for example 12, 24 or 36), "
                "and whether this is for a personal or vehicle purpose."
            )

        if any(word in text for word in ["car", "bike", "vehicle"]):
            return (
                "You’re interested in a vehicle loan. Please share the approximate amount "
                "you need and the tenure in months so I can suggest suitable options."
            )

        return (
            "I can help you with a personalised loan offer. "
            "Tell me roughly how much you need and for how many months, "
            "and I’ll explain the likely EMI and next steps."
        )

    def _fallback_response(self, mode: str) -> str:
        if mode == "objection_handling":
            return "I understand your concern. Let's look at the numbers together to see if we can make this comfortable for you."
        return "Hi! I can help you with personal loans. Share the amount and tenure you are looking for."

