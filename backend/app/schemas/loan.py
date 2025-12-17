from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    """Lightweight in-memory representation of a loan application.

    This is intentionally simple and is meant to back the demo REST
    endpoints described in the edge-case documentation, not a full
    production core-loan system.
    """

    application_id: str
    pan_number: str
    desired_amount: float
    status: str = "INITIATED"  # e.g. INITIATED, ACTIVE, REJECTED, CANCELLED, EXPIRED
    stage: str = "PENDING_DOCUMENT_UPLOAD"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    customer_profile: Dict[str, Any] = Field(default_factory=dict)
    current_offer: Dict[str, Any] = Field(default_factory=dict)
    co_borrower: Dict[str, Any] = Field(default_factory=dict)


class CounterOfferResponse(BaseModel):
    status: str
    message: str
    new_application_id: Optional[str] = None
    new_eligible_amount: Optional[float] = None
    new_monthly_emi: Optional[float] = None
    new_dti_ratio: Optional[str] = None
    new_approval_likelihood: Optional[str] = None
