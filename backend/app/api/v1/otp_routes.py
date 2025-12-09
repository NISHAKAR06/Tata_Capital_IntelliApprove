"""OTP send/verify endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_otp_service, get_orchestrator
from app.orchestrator.state_manager import StateManager
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/send")
def send_otp(conversation_id: str, phone_number: str, otp_service=Depends(get_otp_service)) -> dict:
    record = otp_service.send_otp(phone_number)
    return {"status": "sent", "phone": record.phone_number}


@router.post("/verify", response_model=OrchestratorResponse)
def verify_otp(
    conversation_id: str,
    phone_number: str,
    otp: str,
    otp_service=Depends(get_otp_service),
    orchestrator=Depends(get_orchestrator),
):
    ok = otp_service.verify_otp(phone_number, otp)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    state = StateManager.get_state(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")

    state.kyc.otp_status = "verified"
    req = OrchestratorRequest(state=state, event="otp_verified")
    return orchestrator.handle_request(req)
