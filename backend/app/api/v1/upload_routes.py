"""File upload endpoints (salary slip, documents)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_orchestrator, get_storage_service
from app.orchestrator.state_manager import StateManager
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse
from app.workers.ocr_agent import OcrAgent

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/salary-slip", response_model=OrchestratorResponse)
async def upload_salary_slip(
    conversation_id: str,
    file: UploadFile = File(...),
    storage = Depends(get_storage_service),
    orchestrator = Depends(get_orchestrator),
):
    state = StateManager.get_state(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")

    content = await file.read()
    object_name = storage.upload_bytes(conversation_id=conversation_id, filename=file.filename, data=content)
    file_url = storage.url_for(object_name)

    ocr = OcrAgent()
    result = ocr.extract_salary_slip(file_id=object_name, file_name=file.filename, file_bytes=content)

    state.salary_slip.file_id = object_name
    state.salary_slip.net_monthly_salary = result.net_salary
    state.salary_slip.confidence = result.confidence

    # Hand control back to orchestrator so it can move
    # from DOCUMENT_UPLOAD -> SANCTION based on salary slip.
    req = OrchestratorRequest(state=state, event="document_uploaded")
    resp = await orchestrator.orchestrate(req)
    return resp
