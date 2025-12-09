"""High-level orchestrator coordinating all stages."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from app.config.gemini_client import GeminiClient
from app.orchestrator.decision_engine import compute_emi, compute_personalized_rate, run_underwriting_rules
from app.orchestrator.emotion_detector import EmotionDetector
from app.orchestrator.intent_classifier import IntentClassifier
from app.orchestrator.router import StageRouter
from app.orchestrator.state_manager import StateManager
from app.schemas.audit import AuditEntry
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse, OrchestratorState, StageType
from app.schemas.underwriting import UnderwritingExplainability
from app.services.analytics import AnalyticsTracker
from app.services.bureau_service import BureauService
from app.services.crm_service import CRMService
from app.services.offermart_service import OffermartService
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
        vector_service: Optional[VectorService] = None,
    ) -> None:
        self.state_manager = state_manager
        self.crm = crm_service or CRMService()
        self.bureau = bureau_service or BureauService()
        self.analytics = analytics or AnalyticsTracker()
        self.offers = offer_service or OffermartService()
        self.vectors = vector_service or VectorService()
        self.router = StageRouter()
        self.llm_client = GeminiClient()
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_agent = SanctionAgent()
        self.gamification_engine = GamificationEngine()
        self.pricing_engine = PricingEngine()
        self.scoring_engine = ScoringEngine()

    def handle_request(self, payload: OrchestratorRequest) -> OrchestratorResponse:
        state = payload.state
        conversation_id = state.conversation_id or str(uuid4())
        state.conversation_id = conversation_id
        self._hydrate_crm_snapshot(state)

        stage = self.router.determine_stage(state, payload.event)
        state.stage = stage

        inference_context = self._enrich_state(state, payload)
        explainability = self._maybe_run_underwriting(state)
        worker_payload = self._build_worker_payload(stage, state, explainability)
        message = self._compose_message(stage, state, explainability, payload.user_message, inference_context)

        audit_entry = self._create_audit_entry(stage, payload, worker_payload, message)
        state.audit_log.append(audit_entry.dict())
        self.state_manager.upsert_state(state)

        response = OrchestratorResponse(
            conversation_id=conversation_id,
            stage=stage,
            message_to_user=message,
            invoke_worker={"name": worker_payload["worker"], "payload": worker_payload["payload"]},
            state_updates=state.dict(),
            next_action=self.router.next_action(stage, state),
            explainability=explainability.dict() if explainability else None,
            audit_entry=audit_entry.dict(),
            fallback_needed=state.flags.fallback_needed,
            model_version=self.llm_client.model_version,
        )

        self.analytics.track_event(
            "orchestrator_response",
            {
                "conversation_id": conversation_id,
                "stage": stage,
                "intent": state.last_intent,
                "action": response.next_action,
            },
        )
        return response

    def _hydrate_crm_snapshot(self, state: OrchestratorState) -> None:
        if state.customer_id and not state.kyc.crm_snapshot:
            state.kyc.crm_snapshot = self.crm.get_customer_profile(state.customer_id)

    def _enrich_state(self, state: OrchestratorState, payload: OrchestratorRequest) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        message = payload.user_message or ""
        if message:
            emotion = EmotionDetector.detect(message)
            state.emotion.primary = emotion["primary"]
            state.emotion.confidence = emotion["confidence"]
            intent, confidence = IntentClassifier.classify(message)
            state.last_intent = intent
            context.update({"intent_confidence": confidence})
            transcript_score = self.scoring_engine.score_conversation(message)
            state.flags.fallback_needed = transcript_score["engagement"] < 0.2
            context["engagement"] = transcript_score["engagement"]

        offer_update = self._refresh_offer(state, payload)
        context.update(offer_update)
        return context

    def _refresh_offer(self, state: OrchestratorState, payload: OrchestratorRequest) -> Dict[str, Any]:
        requested_amount = payload.loan_request.get("loan_amount") or state.loan_request.requested_amount or 500000.0
        requested_tenure = payload.loan_request.get("tenure_months") or state.loan_request.requested_tenure or 60
        credit_score = payload.customer_profile.get("credit_score") if payload.customer_profile else None
        loyalty_years = state.kyc.crm_snapshot.get("loyalty_years") if state.kyc.crm_snapshot else None
        auto_debit = bool(state.kyc.crm_snapshot.get("auto_debit_enabled")) if state.kyc.crm_snapshot else False
        utilization_lt_30 = bool(state.kyc.crm_snapshot.get("utilization_lt_30")) if state.kyc.crm_snapshot else False
        is_home_loan_customer = bool(state.kyc.crm_snapshot.get("is_home_loan_customer")) if state.kyc.crm_snapshot else False

        offer = self.pricing_engine.price_offer(
            principal=requested_amount,
            tenure_months=requested_tenure,
            credit_score=credit_score,
            loyalty_years=loyalty_years,
            auto_debit_enabled=auto_debit,
            utilization_lt_30=utilization_lt_30,
            is_home_loan_customer=is_home_loan_customer,
        )
        state.offer.amount = requested_amount
        state.offer.tenure = requested_tenure
        state.offer.personalized_rate = offer["rate"]
        state.offer.emi = offer["emi"]
        state.loan_request.requested_amount = requested_amount
        state.loan_request.requested_tenure = requested_tenure
        return offer

    def _maybe_run_underwriting(self, state: OrchestratorState) -> Optional[UnderwritingExplainability]:
        if state.stage != "UNDERWRITING":
            return None
        bureau_report = self.bureau.fetch_report(state.customer_id)
        state.underwriting["bureau"] = bureau_report.dict()
        explainability = run_underwriting_rules(
            credit_score=bureau_report.score,
            loan_amount=state.offer.amount or 0.0,
            pre_approved_limit=state.underwriting.get("pre_approved_limit"),
            monthly_income=state.salary_slip.net_monthly_salary,
            proposed_emi=state.offer.emi,
        )
        state.underwriting.update(explainability.dict())
        return explainability

    def _build_worker_payload(
        self,
        stage: StageType,
        state: OrchestratorState,
        explainability: Optional[UnderwritingExplainability],
    ) -> Dict[str, Any]:
        payload = {
            "conversation_id": state.conversation_id,
            "stage": stage,
            "intent": state.last_intent,
            "emotion": state.emotion.dict(),
        }
        if explainability:
            payload["explainability"] = explainability.dict()
        worker = self.router.worker_for_stage(stage)
        return {"worker": worker, "payload": payload}

    def _compose_message(
        self,
        stage: StageType,
        state: OrchestratorState,
        explainability: Optional[UnderwritingExplainability],
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        if stage == "SALES":
            # Use the SalesAgent to generate a dynamic response
            sales_context = {
                "offer_amount": state.offer.amount,
                "offer_tenure": state.offer.tenure,
                "offer_rate": state.offer.personalized_rate,
                "offer_emi": state.offer.emi,
                "customer_name": state.kyc.crm_snapshot.get("name") if state.kyc.crm_snapshot else "Customer",
            }
            if context:
                sales_context.update(context)
            return self.sales_agent.craft_pitch(sales_context, user_message or "")

        if stage == "VERIFICATION":
            return "I have triggered an OTP to your registered mobile number. Please verify to continue."
        if stage == "DOCUMENT_UPLOAD":
            return "Please upload your latest salary slip so that underwriting can proceed."
        if stage == "UNDERWRITING" and explainability:
            return explainability.summary or "Underwriting completed."
        if stage == "SANCTION" and state.sanction.sanction_number:
            return (
                f"Congratulations! Sanction letter {state.sanction.sanction_number} is ready. "
                f"Download it before {state.sanction.valid_until}."
            )
        if stage == "GAMIFICATION":
            badge = self.gamification_engine.assign_badge(stage, len(state.audit_log))
            return badge["message"]
        if stage == "ECOSYSTEM_OFFERS":
            offers = self.offers.list_partner_offers()
            return f"Unlocked partner offers: {', '.join(o['partner'] for o in offers)}"
        return "Your journey is on track. Let me know how I can help further."

    def _create_audit_entry(
        self,
        stage: StageType,
        payload: OrchestratorRequest,
        worker_payload: Dict[str, Any],
        message: str,
    ) -> AuditEntry:
        return AuditEntry(
            timestamp=datetime.now(tz=timezone.utc),
            actor="master_orchestrator",
            action=f"stage_{stage.lower()}",
            input_snapshot=payload.dict(),
            output_snapshot={"message": message, "worker": worker_payload["worker"]},
            model_version=self.llm_client.model_version,
        )
