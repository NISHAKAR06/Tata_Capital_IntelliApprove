"""Offer Mart eligibility and offer generation endpoints.

These routes are thin wrappers around the local Offer Mart mock server
exposed via OffermartService so that the backend exposes the
/api/offer-mart/* APIs used in the edge-case test matrix.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_offermart_service
from app.services.offermart_service import OffermartService

router = APIRouter(prefix="/offer-mart", tags=["OfferMart"])


class EligibilityRequest(BaseModel):
    pan_number: str
    monthly_income: float
    credit_score: int
    existing_debt: float
    desired_amount: float
    desired_tenure: Optional[int] = 48


@router.post("/check-eligibility")
def check_eligibility(
    payload: EligibilityRequest,
    offer_service: OffermartService = Depends(get_offermart_service),
) -> Dict[str, Any]:
    """Proxy to Offer Mart mock /check-eligibility.

    Returns the full JSON body from the mock so it matches the
    documentation examples as closely as possible.
    """

    body = offer_service.check_eligibility(payload.model_dump())
    if not body:
        raise HTTPException(status_code=502, detail="Offer Mart service unavailable")
    return body


@router.post("/generate-offers")
def generate_offers(
    payload: EligibilityRequest,
    offer_service: OffermartService = Depends(get_offermart_service),
) -> Dict[str, Any]:
    """Proxy to Offer Mart mock /generate-offers.

    Uses the same request schema as eligibility for convenience.
    """

    body = offer_service.generate_offers(payload.model_dump())
    if not body:
        raise HTTPException(status_code=502, detail="Offer Mart service unavailable")
    return body
