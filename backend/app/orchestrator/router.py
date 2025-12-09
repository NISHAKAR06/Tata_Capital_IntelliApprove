"""Stage routing logic for the orchestrator."""
from __future__ import annotations

from typing import Optional

from app.schemas.conversation_state import ActionType, OrchestratorState, StageType


class StageRouter:
    _stage_flow = [
        "SALES",
        "VERIFICATION",
        "DOCUMENT_UPLOAD",
        "UNDERWRITING",
        "SANCTION",
        "GAMIFICATION",
        "ECOSYSTEM_OFFERS",
        "COMPLETED",
    ]

    _worker_map = {
        "SALES": "sales_agent",
        "VERIFICATION": "verification_agent",
        "DOCUMENT_UPLOAD": "ocr_agent",
        "UNDERWRITING": "underwriting_agent",
        "SANCTION": "sanction_agent",
        "GAMIFICATION": "gamification_engine",
        "ECOSYSTEM_OFFERS": "offermart_service",
        "COMPLETED": "analytics",
    }

    def determine_stage(self, state: OrchestratorState, event: Optional[str]) -> StageType:
        current = state.stage or "SALES"
        if event == "otp_verified":
            return "UNDERWRITING"
        if event == "document_uploaded":
            return "UNDERWRITING"
        if event == "sanction_generated":
            return "SANCTION"
        if event == "loan_disbursed":
            return "COMPLETED"
        return current  # hold stage by default

    def next_action(self, stage: StageType, state: OrchestratorState) -> ActionType:
        if stage == "VERIFICATION" and state.kyc.otp_status != "verified":
            return "request_otp"
        if stage == "DOCUMENT_UPLOAD" and not state.salary_slip.file_id:
            return "request_upload"
        if stage == "UNDERWRITING" and not state.underwriting.get("decision"):
            return "process_salary_slip"
        if stage == "SANCTION" and not state.sanction.sanction_number:
            return "manual_review"
        return "continue"

    def worker_for_stage(self, stage: StageType) -> str:
        return self._worker_map.get(stage, "sales_agent")
