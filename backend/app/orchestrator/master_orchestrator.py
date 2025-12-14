"""High-level orchestrator coordinating all stages."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.emotion_detector import EmotionDetector
from app.orchestrator.intent_classifier import IntentClassifier
from app.orchestrator.state_manager import StateManager
from app.orchestrator.prompts import get_master_system_prompt
from app.schemas.audit import AuditEntry
from app.schemas.conversation_state import EmotionState, OrchestratorRequest, OrchestratorResponse, OrchestratorState, StageType
from app.schemas.underwriting import UnderwritingExplainability
from app.services.analytics import AnalyticsTracker
from app.services.bureau_service import BureauService
from app.services.crm_service import CRMService
from app.services.offermart_service import OffermartService
from app.services.notification_service import NotificationService
from app.services.vector_service import VectorService
from app.utils.time_utils import utc_now_iso
from app.workers.gamification_engine import GamificationEngine
from app.workers.pricing_engine import PricingEngine
from app.workers.sales_agent import SalesAgent
from app.workers.sanction_agent import SanctionAgent
from app.workers.scoring_engine import ScoringEngine
from app.workers.underwriting_agent import UnderwritingAgent
from app.workers.verification_agent import VerificationAgent


class MasterOrchestrator:
    """Entry point invoked by API controllers."""

    def __init__(
        self,
        *,
        state_manager: type[StateManager] = StateManager,
        crm_service: Optional[CRMService] = None,
        bureau_service: Optional[BureauService] = None,
        analytics: Optional[AnalyticsTracker] = None,
        offer_service: Optional[OffermartService] = None,
        notification_service: Optional[NotificationService] = None,
        vector_service: Optional[VectorService] = None,
    ) -> None:
        self.state_manager = state_manager
        settings = get_settings()
        self.crm = crm_service or CRMService()
        self.bureau = bureau_service or BureauService()
        self.analytics = analytics or AnalyticsTracker()
        self.offers = offer_service or OffermartService()
        self.notifications = notification_service or NotificationService()
        self.vectors = vector_service or VectorService()

        # LLM for Master Agent (can use a dedicated fine-tuned Ollama model)
        model_name = settings.ollama_model_master or settings.ollama_model_default
        self.llm_client = OllamaClient(model=model_name)
        self.master_system_prompt = get_master_system_prompt() or (
            "You are 'IntelliApprove', an AI loan assistant for Tata Capital. "
            "Greet the customer warmly and explain in one short paragraph how you can help with personal loans. "
            "Always end by asking how much they need and for how long."
        )
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_agent = SanctionAgent()
        self.gamification_engine = GamificationEngine()
        self.pricing_engine = PricingEngine()
        self.scoring_engine = ScoringEngine()
        self.emotion_detector = EmotionDetector()
        self.intent_classifier = IntentClassifier()

    async def process_message(
        self,
        session_id: str,
        user_input: str,
        language: str = "en",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """High-level helper matching the design doc API.

        This wraps `orchestrate` under the hood, so both REST and WebSocket
        callers can either use the strict OrchestratorRequest schema or this
        simpler signature (session_id + text + language).
        """

        # Load or initialise state
        state = self.state_manager.get_state(session_id) or OrchestratorState(
            conversation_id=session_id,
            language=language,
        )

        req = OrchestratorRequest(
            user_message=user_input,
            state=state,
        )

        resp = await self.orchestrate(req)

        return {
            "type": "ai_message",
            "message": resp.message_to_user,
            "agent": "master",
            "action": resp.next_action,
            "stage": resp.stage,
            "state": resp.state_updates,
            "conversation_id": resp.conversation_id,
        }

    async def orchestrate(self, payload: OrchestratorRequest) -> OrchestratorResponse:
        """
        Master orchestration logic with clear decision points.
        Replaces the previous handle_request logic with the new Decision Tree.
        """
        # 1. Hydrate / initialise state
        state = payload.state
        if not state.conversation_id:
            state.conversation_id = f"conv_{uuid4().hex[:10]}"
        user_input = payload.user_message or ""
        
        # Ensure CRM / customer data is present
        if not state.customer_profile:
            # If the caller passed a customer_profile with an id, hydrate it via CRMService
            incoming_profile = payload.customer_profile or {}
            customer_id = incoming_profile.get("customer_id")

            if customer_id:
                # Use the lightweight CRM mock to fetch a richer snapshot
                state.customer_profile = self.crm.get_customer_profile(customer_id)
            elif incoming_profile:
                # Fallback: trust whatever structured profile the caller provided
                state.customer_profile = incoming_profile
            else:
                # Demo fallback when no profile is provided
                self._hydrate_crm_snapshot(state)

        # 2. Analyze Input
        emotion_result = self.emotion_detector.detect(user_input)
        intent_name, intent_conf = self.intent_classifier.classify(user_input)
        
        # Language Detection (Simple)
        if "english" in user_input.lower() and "tell" in user_input.lower():
            state.language = "en"
        elif "hindi" in user_input.lower() or "hinglish" in user_input.lower():
            state.language = "hi"

        state.last_intent = intent_name

        # Normalise emotion into EmotionState for clean Pydantic serialization
        if isinstance(emotion_result, EmotionState):
            state.emotion = emotion_result
        elif isinstance(emotion_result, dict):
            # Pydantic will coerce, but doing it explicitly avoids warnings
            state.emotion = EmotionState(**emotion_result)
        else:
            state.emotion = EmotionState()

        # 3. Decision Tree Execution
        response_message = ""
        worker_action = None
        
        # Initialize stage if None
        if state.stage is None:
            state.stage = "NEW"

        next_stage = state.stage

        # DECISION POINT 1: New Conversation
        if state.stage == "NEW":
            next_stage = "GREETING"
            # Prefer an LLM-generated greeting so the experience is truly
            # agentic, but fall back to a fixed copy if Ollama is not
            # available or fails.
            if self.llm_client.available:
                llm_greeting = self.llm_client.generate(
                    system_prompt=self.master_system_prompt,
                    user_prompt=(
                        "A new customer has just opened the chat window but "
                        "has not typed anything yet. Start the conversation."
                    ),
                    max_tokens=160,
                )
                response_message = llm_greeting or (
                    "Hi, I'm IntelliApprove, your AI loan assistant from Tata Capital. "
                    "I can help you explore personal loan options tailored to you. "
                    "To get started, tell me how much you need and for how long."
                )
            else:
                response_message = (
                    "Hi, I'm IntelliApprove, your AI loan assistant from Tata Capital. "
                    "I can help you explore personal loan options tailored to you. "
                    "To get started, tell me how much you need and for how long."
                )
            state.stage = next_stage

        # DECISION POINT 2: Greeting Response
        elif state.stage == "GREETING":
            if intent_name in ['positive_interest', 'ask_loan', 'proceed_agreement']:
                next_stage = "SALES"
                response_message = self.sales_agent.craft_pitch(
                    context=state.dict(), 
                    user_message=user_input, 
                    mode='needs_discovery'
                )
            elif intent_name == 'negative':
                response_message = "No problem! I'm here if you need funds later. Have a great day!"
                next_stage = "COMPLETED"
            elif intent_name == 'ask_rate' or intent_name == 'ask_emi':
                 response_message = self.sales_agent.craft_pitch(
                    context=state.dict(), 
                    user_message=user_input, 
                    mode='information_only'
                )
            else:
                 # Default fallthrough to sales
                 next_stage = "SALES"
                 response_message = self.sales_agent.craft_pitch(context=state.dict(), user_message=user_input, mode='needs_discovery')

        # DECISION POINT 3: Sales Engagement
        elif state.stage == "SALES":
            # Sub-decision 3A: Objections?
            primary_emotion = None
            if isinstance(emotion_result, dict):
                primary_emotion = emotion_result.get("primary") or emotion_result.get("emotion")

            if primary_emotion in ['anxiety', 'concern', 'confusion', 'sadness']:
                concern_type = 'affordability_anxiety' if 'emi' in user_input.lower() or 'expensive' in user_input.lower() else 'general_concern'
                
                # Get objection handling data
                objection_data = {}
                if concern_type == 'affordability_anxiety':
                    objection_data = self.sales_agent.handle_affordability_objection(state.customer_profile, state.loan_request.dict())
                
                response_message = self.sales_agent.craft_pitch(
                    context={**state.dict(), **objection_data},
                    user_message=user_input,
                    mode='objection_handling',
                    concern_type=concern_type
                )
            
            # Sub-decision 3B: Agreement?
            elif intent_name in ['proceed_agreement', 'positive_interest']:
                next_stage = "VERIFICATION"
                response_message = "Great! Let's proceed. I've sent an OTP to your registered mobile number ending in 8899. Please enter it."
            
            # Sub-decision 3C: Modification?
            elif intent_name == 'modification_request':
                response_message = self.sales_agent.craft_pitch(
                    context=state.dict(),
                    user_message=user_input,
                    mode='renegotiation',
                    modification={'request': user_input}
                )
            else:
                # Continue conversation
                response_message = self.sales_agent.craft_pitch(context=state.dict(), user_message=user_input, mode='needs_discovery')

        # DECISION POINT 4: Verification
        elif state.stage == "VERIFICATION":
            if intent_name == 'otp_submission' or (user_input.isdigit() and len(user_input) == 4):
                # Simple OTP check (4-digit demo OTP). In a full
                # implementation this would call OTPService / Redis.
                next_stage = "UNDERWRITING"

                # Mark KYC as verified in state
                state.kyc.otp_status = "verified"
                state.kyc.verified = True
                if not state.kyc.phone_mask:
                    state.kyc.phone_mask = "XXXX8899"

                # Generate a short KYC verification summary
                verification_context = {
                    "name": state.customer_profile.get("name"),
                    "customer_id": state.customer_profile.get("customer_id"),
                    "phone_mask": state.kyc.phone_mask,
                    "kyc_status": "verified",
                }
                kyc_message = self.verification_agent.summarize_checks(verification_context)

                # DECISION POINT 5: Underwriting
                # Call mock bureau to attach a bureau snapshot for explainability
                try:
                    bureau_report = self.bureau.fetch_report(state.customer_profile.get("pan"))
                    # Persist bureau snapshot for explainability
                    state.underwriting["bureau_report"] = bureau_report.dict()
                    # Also surface credit_score on the customer profile for downstream agents
                    state.customer_profile["credit_score"] = bureau_report.score
                except Exception:
                    # Non-fatal: underwriting can proceed without bureau details
                    pass

                # Edge Case #1: Credit Score Check
                credit_eval = self.underwriting_agent.evaluate_credit_score(state.customer_profile)
                
                if credit_eval['decision'] == 'REJECTED':
                    next_stage = "REJECTED"
                    summary = (
                        "Thank you for waiting. Unfortunately, we cannot approve the loan at this time. "
                        f"Reason: {credit_eval.get('reason')}. "
                        "Here are some steps that can improve your approval chances over the next few months: "
                        "reduce existing EMIs, keep credit card utilization low, and avoid new enquiries."
                    )
                    explain_payload = {
                        "decision": "rejected",
                        "summary": summary,
                        "factors": [
                            {
                                "name": "credit_score",
                                "value": str(credit_eval.get("credit_score")),
                                "threshold": ">= 700",
                                "status": "fail",
                                "reason": "Credit score below minimum threshold.",
                            }
                        ],
                    }
                    underwriting_message = self.underwriting_agent.explain_decision(explain_payload)
                    response_message = f"{kyc_message} {underwriting_message or summary}"
                else:
                    # Edge Case #2: Conditional Approval
                    loan_req = state.loan_request.dict()
                    if not loan_req.get("amount"):
                        # For demo, fall back to either offer amount or a default
                        loan_req["amount"] = state.offer.amount or 500000
                    
                    approval_eval = self.underwriting_agent.evaluate_conditional_approval(state.customer_profile, loan_req)
                    
                    if approval_eval['decision'] == 'CONDITIONAL_APPROVAL':
                        next_stage = "DOCUMENT_UPLOAD"
                        response_message = (
                            f"{kyc_message} "
                            f"Good news! Your credit score is excellent. "
                            f"Since you requested ₹{loan_req['amount']}, which is above your pre-approved limit, "
                            "I just need your latest salary slip to verify affordability."
                        )
                    elif approval_eval['decision'] == 'INSTANT_APPROVAL':
                        next_stage = "SANCTION"
                        response_message = (
                            f"{kyc_message} "
                            "Congratulations! Your loan is fully approved. Here is your sanction letter."
                        )
                    else:
                        next_stage = "REJECTED"
                        rejection_summary = "We could not approve the requested amount."
                        explain_payload = {
                            "decision": "rejected",
                            "summary": rejection_summary,
                            "factors": [],
                        }
                        underwriting_message = self.underwriting_agent.explain_decision(explain_payload)
                        response_message = f"{kyc_message} {underwriting_message or rejection_summary}"

            elif intent_name == 'kyc_mismatch':
                response_message = "I've noted that. Connecting you to a human agent to update KYC."
                next_stage = "COMPLETED" # Handoff
            else:
                response_message = "Please enter the 4-digit OTP sent to your mobile."

        # DECISION POINT 6: Document Collection
        elif state.stage == "DOCUMENT_UPLOAD":
            # Triggered when salary slip has been uploaded via /upload/salary-slip
            if payload.event == "document_uploaded" and state.salary_slip.net_monthly_salary:
                response_message = "Analyzing your salary slip... [Processing]..."

                salary_data = {
                    "net_monthly_salary": state.salary_slip.net_monthly_salary,
                    "employer": state.customer_profile.get("employer") or "",
                }

                loan_req = state.loan_request.dict()
                if not loan_req.get("amount"):
                    loan_req["amount"] = state.offer.amount or 500000
                if not loan_req.get("emi"):
                    loan_req["emi"] = state.offer.emi or 0

                decision = self.underwriting_agent.reevaluate_with_salary(
                    state.customer_profile,
                    loan_req,
                    salary_data,
                )

                if decision.get("decision") == "APPROVED":
                    next_stage = "SANCTION"
                    response_message = (
                        f"Excellent! Salary verified (₹{salary_data['net_monthly_salary']}). "
                        f"Your EMI is comfortable ({decision.get('emi_to_income_ratio'):.1f}% of income). "
                        "Loan APPROVED!"
                    )
                else:
                    summary = (
                        "We could not approve the full amount based on the salary slip. "
                        f"{decision.get('reason', 'Please talk to a human agent for options.') }"
                    )
                    explain_payload = {
                        "decision": decision.get("decision"),
                        "summary": summary,
                        "factors": [],
                    }
                    underwriting_message = self.underwriting_agent.explain_decision(explain_payload)
                    response_message = underwriting_message or summary
            else:
                response_message = "Please upload your salary slip (PDF/Image) to proceed."

        # DECISION POINT 7: Sanction
        elif state.stage == "SANCTION":
            # Generate a local sanction letter PDF and summarize it for the user
            loan_details = {
                "amount": state.offer.amount or state.loan_request.requested_amount,
                "tenure": state.offer.tenure or state.loan_request.requested_tenure,
                "emi": state.offer.emi,
                "rate": state.offer.personalized_rate or state.offer.standard_rate,
            }

            sanction_meta = self.sanction_agent.generate_letter(state.customer_profile, loan_details)

            state.sanction.sanction_number = sanction_meta.get("sanction_number")
            state.sanction.pdf_url = sanction_meta.get("file_path")
            state.sanction.valid_until = sanction_meta.get("valid_until")

            summary_payload = {
                "customer": state.customer_profile,
                "loan": loan_details,
                "sanction": sanction_meta,
            }

            summary_message = self.sanction_agent.format_summary(summary_payload)

            # Fire-and-forget notification via mock notification server
            try:
                customer = state.customer_profile or {}
                self.notifications.send_sanction_notification(
                    email=customer.get("email"),
                    phone=customer.get("phone"),
                    customer_name=customer.get("name", "Valued Customer"),
                    amount=loan_details["amount"] or 0.0,
                    tenure_months=loan_details["tenure"] or 0,
                    rate=loan_details["rate"] or 0.0,
                    sanction_number=state.sanction.sanction_number or "UNKNOWN",
                )
            except Exception:
                # Do not break chat flow if notification fails
                pass
            next_stage = "COMPLETED"
            response_message = summary_message or (
                "Thank you! Your sanction letter has been generated and saved to your documents. "
                "Funds will be disbursed in 2 hours."
            )

        # Fallback
        else:
            response_message = self.sales_agent.craft_pitch(context=state.dict(), user_message=user_input, mode='needs_discovery')

        # Update State
        state.stage = next_stage

        # Append a lightweight audit trail of the conversation turn so
        # that the full chatbot message history is stored alongside the
        # loan pipeline state (in Redis / DB via StateManager).
        audit_entry = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            actor="system",
            action="orchestrate_turn",
            input_snapshot={
                "user_message": user_input,
                "stage_before": state.stage,
                "intent": intent_name,
            },
            output_snapshot={
                "message_to_user": response_message,
                "next_stage": next_stage,
            },
            model_version=self.llm_client.model_version,
        )
        try:
            state.audit_log.append(audit_entry.model_dump())
        except Exception:
            # If audit logging fails, don't break the main flow.
            pass

        self.state_manager.upsert_state(state)
        
        # Determine next_action and invoke_worker
        action = "continue"
        worker_info = {"name": "orchestrator", "payload": {}}

        if next_stage == "VERIFICATION" and "OTP" in response_message:
             action = "request_otp"
        elif next_stage == "DOCUMENT_UPLOAD":
             action = "request_upload"
        elif next_stage == "COMPLETED":
             action = "end"
        elif next_stage == "REJECTED":
             action = "end"
        
        # Construct Response
        return OrchestratorResponse(
            conversation_id=state.conversation_id,
            stage=state.stage,
            message_to_user=response_message,
            state_updates=state.dict(),
            model_version=self.llm_client.model_version,
            invoke_worker=worker_info,
            audit_entry=audit_entry.model_dump(),
            next_action=action,
        )

    def _hydrate_crm_snapshot(self, state: OrchestratorState) -> None:
        """Populate basic customer profile for demo flows."""
        if not state.customer_profile:
            # In real implementation, this would call self.crm.get_customer_profile
            state.customer_profile = {
                "name": "Rajesh Kumar",
                "customer_id": "CUST001",
                "pre_approved_limit": 300000,
                "monthly_income": 80000,
                "credit_score": 750,
                "existing_loans": [{"type": "Auto Loan", "emi": 10000}],
            }
