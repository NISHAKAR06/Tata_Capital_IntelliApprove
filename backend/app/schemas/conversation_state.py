from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

StageType = Literal[
    "NEW",
    "GREETING",
    "SALES",
    "VERIFICATION",
    "UNDERWRITING",
    "DOCUMENT_UPLOAD",
    "SANCTION",
    "GAMIFICATION",
    "ECOSYSTEM_OFFERS",
    "COMPLETED",
    "REJECTED",
]

ActionType = Literal[
    "continue",
    "request_upload",
    "request_otp",
    "process_salary_slip",
    "human_handoff",
    "manual_review",
    "end",
]


class EmotionState(BaseModel):
    primary: Literal["joy", "neutral", "anxiety", "anger", "sadness", "confusion"] = "neutral"
    confidence: float = 0.0


class LoanRequest(BaseModel):
    requested_amount: Optional[float] = None
    requested_tenure: Optional[int] = None
    purpose: Optional[str] = None


class OfferDetails(BaseModel):
    amount: Optional[float] = None
    tenure: Optional[int] = None
    personalized_rate: Optional[float] = None
    emi: Optional[float] = None
    standard_rate: Optional[float] = None
    adjustments: Optional[list] = Field(default_factory=list)


class KYCDetails(BaseModel):
    otp_status: Optional[str] = "pending"
    verified: bool = False
    phone_mask: Optional[str] = None
    crm_snapshot: Dict[str, Any] = Field(default_factory=dict)


class SalarySlipState(BaseModel):
    file_id: Optional[str] = None
    net_monthly_salary: Optional[float] = None
    confidence: Optional[float] = None


class SanctionState(BaseModel):
    sanction_number: Optional[str] = None
    pdf_url: Optional[str] = None
    valid_until: Optional[str] = None


class FlagState(BaseModel):
    needs_human: bool = False
    fallback_needed: bool = False
    abandoned: bool = False


class OrchestratorState(BaseModel):
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None
    language: Literal["en", "hi", "ta", "te", "bn", "mr"] = "en"
    stage: Optional[StageType] = None
    last_intent: Optional[str] = None
    emotion: EmotionState = Field(default_factory=EmotionState)
    loan_request: LoanRequest = Field(default_factory=LoanRequest)
    offer: OfferDetails = Field(default_factory=OfferDetails)
    kyc: KYCDetails = Field(default_factory=KYCDetails)
    underwriting: Dict[str, Any] = Field(default_factory=dict)
    salary_slip: SalarySlipState = Field(default_factory=SalarySlipState)
    sanction: SanctionState = Field(default_factory=SanctionState)
    flags: FlagState = Field(default_factory=FlagState)
    audit_log: list = Field(default_factory=list)


class OrchestratorRequest(BaseModel):
    user_message: Optional[str] = None
    state: OrchestratorState = Field(default_factory=OrchestratorState)
    customer_profile: Dict[str, Any] = Field(default_factory=dict)
    loan_request: Dict[str, Any] = Field(default_factory=dict)
    event: Optional[str] = None
    uploaded_document_type: Optional[str] = None


class OrchestratorResponse(BaseModel):
    conversation_id: Optional[str]
    stage: StageType
    message_to_user: str
    invoke_worker: Dict[str, Any]
    state_updates: Dict[str, Any]
    next_action: ActionType
    explainability: Optional[Dict[str, Any]] = None
    audit_entry: Optional[Dict[str, Any]] = None
    fallback_needed: bool = False
    model_version: Optional[str] = None
