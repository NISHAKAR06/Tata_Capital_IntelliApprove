"""Sanction generation and acceptance endpoints."""
from __future__ import annotations

from datetime import datetime, timedelta
import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_pdf_service
from app.orchestrator.state_manager import StateManager
from app.services.notification_service import NotificationService
from app.schemas.conversation_state import OrchestratorResponse
from app.schemas.sanction_letter import SanctionLetter
from app.utils.time_utils import utc_now_iso

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


@router.post("/accept")
def accept_sanction(conversation_id: str) -> Dict[str, Any]:
    """Record sanction acceptance and simulate fund disbursement.

    This models the final stages of the journey where the customer signs the
    sanction letter and funds are transferred to their bank account. The
    actual banking integration is mocked with a generated transaction id.
    """

    state = StateManager.get_state(conversation_id)
    if not state or not state.sanction.sanction_number:
        raise HTTPException(status_code=400, detail="No sanction letter found for this conversation")

    amount = float(state.offer.amount or 0.0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Missing sanctioned amount")

    processing_fee = round(amount * 0.01, 2)
    net_disbursal = round(amount - processing_fee, 2)
    txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

    state.sanction.accepted = True
    state.sanction.disbursed = True
    state.sanction.disbursement_amount = net_disbursal
    state.sanction.disbursement_reference = txn_id
    state.sanction.disbursed_at = utc_now_iso()
    StateManager.upsert_state(state)

    # Fire-and-forget disbursement notification via mock notification server
    try:
        customer = (state.customer_profile or {}) if state else {}
        notif = NotificationService()
        notif.send_disbursement_confirmation(
            email=customer.get("email"),
            phone=customer.get("phone"),
            customer_name=customer.get("name", "Valued Customer"),
            net_amount=net_disbursal,
            txn_id=txn_id,
        )
    except Exception:
        pass

    return {
        "status": "success",
        "transaction_id": txn_id,
        "gross_amount": amount,
        "processing_fee": processing_fee,
        "net_disbursed": net_disbursal,
        "disbursed_at": state.sanction.disbursed_at,
        "message": (
            "Sanction letter accepted and funds disbursed. "
            f"Net amount of ₹{net_disbursal:,.0f} will reflect in the registered bank account "
            "within standard processing timelines."
        ),
    }
