"""Conversation orchestration endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_logger, get_orchestrator
from app.orchestrator.state_manager import StateManager
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/orchestrate", response_model=OrchestratorResponse)
def orchestrate(
    payload: OrchestratorRequest,
    orchestrator = Depends(get_orchestrator),
):
    logger = get_logger()
    response = orchestrator.handle_request(payload)
    logger.debug("orchestrated conversation", extra={"conversation_id": response.conversation_id})
    return response


@router.get("/state/{conversation_id}", response_model=OrchestratorResponse)
def get_state(conversation_id: str):
    state = StateManager.get_state(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")

    empty_request = OrchestratorRequest(state=state)
    return OrchestratorResponse(
        conversation_id=state.conversation_id,
        stage=state.stage or "NEW",
        message_to_user="State snapshot returned",
        invoke_worker={},
        state_updates=state.dict(),
        next_action="continue",
    )
