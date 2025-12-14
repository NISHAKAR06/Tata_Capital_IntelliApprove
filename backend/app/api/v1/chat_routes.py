"""Conversation orchestration endpoints (text + voice)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_audio_service, get_logger, get_orchestrator
from app.orchestrator.state_manager import StateManager
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse, OrchestratorState

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate(
    payload: OrchestratorRequest,
    orchestrator = Depends(get_orchestrator),
):
    """Run a single orchestration step.

    If the client passes only a conversation_id inside `payload.state`, we
    hydrate the full state from StateManager so the journey continues from the
    previous stage instead of restarting from NEW on every turn.
    """
    logger = get_logger()

    # Hydrate existing state when a conversation_id is provided
    conv_id = payload.state.conversation_id
    if conv_id:
        existing = StateManager.get_state(conv_id)
        if existing:
            # Preserve language override from payload if explicitly set
            if payload.state.language and payload.state.language != existing.language:
                existing.language = payload.state.language
            payload.state = existing

    response = await orchestrator.orchestrate(payload)
    logger.debug("orchestrated conversation", extra={"conversation_id": response.conversation_id})
    return response


@router.post("/voice", response_model=OrchestratorResponse)
async def orchestrate_voice(
    file: UploadFile = File(...),
    conversation_id: str | None = None,
    orchestrator = Depends(get_orchestrator),
    audio_service = Depends(get_audio_service),
):
    """Voice entrypoint.

    Accepts an audio file, transcribes it using AudioService, then routes the
    resulting text through the same master orchestrator so that voice and text
    journeys share identical business logic and cached conversation state.
    """
    logger = get_logger()

    audio_bytes = await file.read()
    transcript_payload = audio_service.transcribe(audio_bytes)
    user_text = (transcript_payload or {}).get("transcript") or ""
    language = (transcript_payload or {}).get("language") or "en"

    # Start from existing state when a conversation_id is provided
    state: OrchestratorState
    if conversation_id:
        existing = StateManager.get_state(conversation_id)
        if existing:
            state = existing
            state.language = language or state.language
        else:
            state = OrchestratorState(conversation_id=conversation_id, language=language)
    else:
        state = OrchestratorState(language=language)

    req = OrchestratorRequest(user_message=user_text, state=state)
    resp = await orchestrator.orchestrate(req)

    # Surface the recognized transcript back to the client so the
    # frontend can show the user's spoken text as a chat bubble.
    if user_text:
        invoke = dict(resp.invoke_worker or {})
        invoke["user_transcript"] = user_text
        resp.invoke_worker = invoke

    logger.debug(
        "orchestrated voice conversation",
        extra={"conversation_id": resp.conversation_id, "transcript": user_text},
    )
    return resp


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
