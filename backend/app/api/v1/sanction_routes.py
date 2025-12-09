"""Sanction generation endpoints."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_pdf_service
from app.orchestrator.state_manager import StateManager
from app.schemas.conversation_state import OrchestratorResponse
from app.schemas.sanction_letter import SanctionLetter

router = APIRouter(prefix="/sanction", tags=["Sanction"])


@router.post("/generate", response_model=SanctionLetter)
def generate_sanction(conversation_id: str, pdf_service=Depends(get_pdf_service)) -> SanctionLetter:
    state = StateManager.get_state(conversation_id)
    if not state or not state.offer.amount or not state.offer.personalized_rate or not state.offer.emi:
        raise HTTPException(status_code=400, detail="Missing offer details")

    payload = {
        "amount": float(state.offer.amount),
        "tenure_months": int(state.offer.tenure or 60),
        "rate_percent": float(state.offer.personalized_rate),
        "emi": float(state.offer.emi),
        "valid_until": (datetime.utcnow() + timedelta(days=7)).date().isoformat(),
    }
    out = pdf_service.generate_sanction_letter(payload)

    state.sanction.sanction_number = str(out["sanction_number"])
    state.sanction.pdf_url = str(out["pdf_url"])
    state.sanction.valid_until = str(out["valid_until"]) if "valid_until" in out else payload["valid_until"]
    StateManager.upsert_state(state)

    return SanctionLetter(
        sanction_number=state.sanction.sanction_number,
        amount=payload["amount"],
        tenure_months=payload["tenure_months"],
        rate_percent=payload["rate_percent"],
        emi=payload["emi"],
        pdf_url=state.sanction.pdf_url,
        valid_until=state.sanction.valid_until,
    )
