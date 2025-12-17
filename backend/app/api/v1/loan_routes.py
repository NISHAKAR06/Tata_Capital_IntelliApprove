"""Loan application routes."""
from __future__ import annotations

from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas.loan import LoanApplication

router = APIRouter(prefix="/loans", tags=["Loans"])

# In-memory storage for demo purposes
LOAN_APPLICATIONS: Dict[str, LoanApplication] = {}


@router.post("/apply", response_model=LoanApplication)
def create_loan_application(payload: LoanApplication) -> LoanApplication:
    """Create a new loan application (demo)."""
    # In a real app, we would save to DB here.
    # For now, we just store in memory.
    
    # If ID is not provided or empty, generate one
    if not payload.application_id:
        payload.application_id = str(uuid4())
        
    LOAN_APPLICATIONS[payload.application_id] = payload
    return payload


@router.get("/{application_id}", response_model=LoanApplication)
def get_loan_application(application_id: str) -> LoanApplication:
    """Get loan application details by ID."""
    if application_id not in LOAN_APPLICATIONS:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    return LOAN_APPLICATIONS[application_id]


@router.get("/", response_model=Dict[str, LoanApplication])
def list_loan_applications() -> Dict[str, LoanApplication]:
    """List all loan applications (debug/demo)."""
    return LOAN_APPLICATIONS
