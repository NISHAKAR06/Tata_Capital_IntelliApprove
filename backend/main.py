from typing import Any, Dict, Literal, Optional, Tuple

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from llm_client import LLMClient

# ----- Types -----


StageType = Literal[
    "SALES",
    "VERIFICATION",
    "UNDERWRITING",
    "SANCTION",
    "GAMIFICATION",
    "ECOSYSTEM_OFFERS",
]

ActionType = Literal[
    "continue",
    "request_upload",
    "end",
    "process_salary_slip",
    "human_handoff",
]


class OrchestratorState(BaseModel):
    stage: Optional[StageType] = None
    loan_amount: Optional[float] = None
    tenure: Optional[int] = None  # in months
    personalized_rate: Optional[float] = None
    emi: Optional[float] = None
    pre_approved_limit: Optional[float] = None
    crm_data: Optional[Dict[str, Any]] = None
    kyc_verified: Optional[bool] = None
    credit_score: Optional[int] = None
    explainability: Optional[Dict[str, Any]] = None
    sanction_data: Optional[Dict[str, Any]] = None


class OrchestratorRequest(BaseModel):
    user_message: Optional[str] = None
    stage: Optional[StageType] = None
    state: OrchestratorState = Field(default_factory=OrchestratorState)
    customer_profile: Optional[Dict[str, Any]] = None
    loan_request: Optional[Dict[str, Any]] = None
    event: Optional[str] = None  # e.g. "document_uploaded", "otp_verified"
    uploaded_document_type: Optional[str] = None  # e.g. "salary_slip"


class OrchestratorResponse(BaseModel):
    stage: StageType
    message_to_user: str
    worker_called: str
    worker_payload: Dict[str, Any]
    state_updates: Dict[str, Any]
    action: ActionType
    fallback_needed: bool = False
    model_version: Optional[str] = None


# ----- Core business logic (pure functions) -----


def compute_personalized_rate(
    base_rate: float,
    credit_score: Optional[int] = None,
    loyalty_years: Optional[int] = None,
    auto_debit_enabled: bool = False,
    utilization_lt_30: bool = False,
    is_home_loan_customer: bool = False,
    floor_rate: float = 9.0,
) -> float:
    rate = base_rate

    if credit_score is not None and credit_score >= 780:
        rate -= 1.5
    if loyalty_years is not None and loyalty_years >= 5:
        rate -= 0.5
    if auto_debit_enabled:
        rate -= 0.3
    if utilization_lt_30:
        rate -= 0.3
    if is_home_loan_customer:
        rate -= 0.4

    if rate < floor_rate:
        rate = floor_rate

    return round(rate, 2)


def compute_emi(
    principal: float,
    annual_rate_percent: float,
    tenure_months: int,
) -> float:
    """
    Standard EMI formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    where:
    - P = principal
    - r = monthly interest rate
    - n = number of months
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    r = annual_rate_percent / 12 / 100
    n = tenure_months

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

    return round(emi, 2)


def run_underwriting_rules(
    credit_score: Optional[int],
    loan_amount: float,
    pre_approved_limit: Optional[float],
    monthly_income: Optional[float],
    proposed_emi: Optional[float],
) -> Dict[str, Any]:
    """
    Implements underwriting rule engine with explainability object.
    """
    explainability: Dict[str, Any] = {
        "decision": None,
        "factors": [],
        "summary": "",
    }

    # Factor: credit score
    if credit_score is None:
        explainability["factors"].append(
            {
                "name": "credit_score",
                "status": "fail",
                "value": None,
                "threshold": "≥ 700",
                "reason": "Credit score missing",
            }
        )
        explainability["decision"] = "rejected"
        explainability["summary"] = "Rejected due to missing credit score."
        return explainability

    if credit_score < 700:
        explainability["factors"].append(
            {
                "name": "credit_score",
                "status": "fail",
                "value": credit_score,
                "threshold": "≥ 700",
                "reason": "Credit score below minimum threshold.",
            }
        )
        explainability["decision"] = "rejected"
        explainability["summary"] = "Rejected because credit score is below 700."
        return explainability
    else:
        explainability["factors"].append(
            {
                "name": "credit_score",
                "status": "pass",
                "value": credit_score,
                "threshold": "≥ 700",
                "reason": "Credit score meets minimum threshold.",
            }
        )

    # Factor: pre-approved limit
    if pre_approved_limit is not None:
        if loan_amount > 2 * pre_approved_limit:
            explainability["factors"].append(
                {
                    "name": "loan_vs_preapproved",
                    "status": "fail",
                    "value": loan_amount,
                    "threshold": f"≤ 2 × {pre_approved_limit}",
                    "reason": "Requested amount exceeds 2× pre-approved limit.",
                }
            )
            explainability["decision"] = "rejected"
            explainability["summary"] = (
                "Rejected because requested amount exceeds 2× pre-approved limit."
            )
            return explainability

        if loan_amount <= pre_approved_limit:
            explainability["factors"].append(
                {
                    "name": "loan_vs_preapproved",
                    "status": "pass",
                    "value": loan_amount,
                    "threshold": f"≤ {pre_approved_limit}",
                    "reason": "Loan amount within pre-approved limit.",
                }
            )
        else:
            explainability["factors"].append(
                {
                    "name": "loan_vs_preapproved",
                    "status": "conditional",
                    "value": loan_amount,
                    "threshold": f"> {pre_approved_limit} and ≤ 2 × {pre_approved_limit}",
                    "reason": "Loan between pre-approved and 2× limit – salary slip required.",
                }
            )
    else:
        explainability["factors"].append(
            {
                "name": "loan_vs_preapproved",
                "status": "unknown",
                "value": loan_amount,
                "threshold": "pre_approved_limit missing",
                "reason": "Pre-approved limit not available.",
            }
        )

    # Factor: DTI (Debt-to-Income via EMI/Salary)
    if monthly_income is None or proposed_emi is None or proposed_emi <= 0:
        explainability["factors"].append(
            {
                "name": "dti_ratio",
                "status": "unknown",
                "value": None,
                "threshold": "EMI / Salary ≤ 50%",
                "reason": "Monthly income or EMI missing.",
            }
        )
        explainability["decision"] = "rejected"
        explainability["summary"] = (
            "Rejected because income or EMI data is missing for DTI calculation."
        )
        return explainability

    dti_ratio = proposed_emi / monthly_income
    dti_percent = round(dti_ratio * 100, 2)

    if dti_ratio <= 0.5:
        explainability["factors"].append(
            {
                "name": "dti_ratio",
                "status": "pass",
                "value": f"{dti_percent}%",
                "threshold": "≤ 50%",
                "reason": "EMI within 50% of income.",
            }
        )
        explainability["decision"] = "approved"
        explainability["summary"] = (
            "Approved: credit score is acceptable and EMI is within 50% of income."
        )
    else:
        explainability["factors"].append(
            {
                "name": "dti_ratio",
                "status": "fail",
                "value": f"{dti_percent}%",
                "threshold": "≤ 50%",
                "reason": "EMI exceeds 50% of income.",
            }
        )
        explainability["decision"] = "rejected"
        explainability["summary"] = (
            "Rejected: EMI exceeds 50% of declared monthly income."
        )

    return explainability


# ----- LLM helper -----


llm_client = LLMClient()


def maybe_llm_rewrite(message: str, state: OrchestratorState) -> Tuple[str, Optional[str]]:
    """
    Optionally rewrite the user-facing message using GPT-5.1-Codex-Max (Preview).
    Keeps deterministic fallback if LLM is unavailable or errors.
    """

    _ = state  # placeholder to keep signature future-proof and avoid unused warnings

    if not message or not llm_client.available:
        return message, None

    system_prompt = (
        "You are Tata Capital's personal loan assistant. Rewrite the following"
        " message to be concise, under 400 characters, and keep all numeric"
        " values, stage names, and instructions intact. Do not invent new"
        " offers, rates, or stages. Maintain a professional, friendly tone."
    )

    candidate = llm_client.generate(
        system_prompt=system_prompt,
        user_message=message,
        max_tokens=220,
    )

    if candidate:
        return candidate, llm_client.model_version

    return message, None


# ----- FastAPI app and orchestrator endpoint -----


app = FastAPI(title="Tata Capital Agentic Loan Orchestrator")

# Allow frontend origins during development; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str = "ok"


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/orchestrate", response_model=OrchestratorResponse)
def orchestrate(payload: OrchestratorRequest) -> OrchestratorResponse:
    """
    Master orchestrator entrypoint.
    NOTE: This is a deterministic rule-based skeleton.
    Actual LLM / LangGraph worker calls should be wired behind worker_called.
    """
    state = payload.state
    stage: StageType = payload.stage or state.stage or "SALES"

    # Default response shell
    resp: Dict[str, Any] = {
        "stage": stage,
        "message_to_user": "",
        "worker_called": "",
        "worker_payload": {},
        "state_updates": {},
        "action": "continue",
        "fallback_needed": False,
    }

    # --- Stage: SALES ---
    if stage == "SALES":
        base_rate = 11.5
        credit_score = state.credit_score or (
            payload.customer_profile or {}
        ).get("credit_score")

        loyalty_years = (payload.customer_profile or {}).get("loyalty_years")
        auto_debit = bool((payload.customer_profile or {}).get("auto_debit_enabled"))
        utilization_lt_30 = bool(
            (payload.customer_profile or {}).get("utilization_lt_30")
        )
        is_home_loan_customer = bool(
            (payload.customer_profile or {}).get("is_home_loan_customer")
        )

        loan_amount = (
            (payload.loan_request or {}).get("loan_amount")
            or state.loan_amount
            or 0.0
        )
        tenure = (
            (payload.loan_request or {}).get("tenure_months")
            or state.tenure
            or 60
        )

        personalized_rate = compute_personalized_rate(
            base_rate=base_rate,
            credit_score=credit_score,
            loyalty_years=loyalty_years,
            auto_debit_enabled=auto_debit,
            utilization_lt_30=utilization_lt_30,
            is_home_loan_customer=is_home_loan_customer,
        )
        emi = compute_emi(
            principal=loan_amount,
            annual_rate_percent=personalized_rate,
            tenure_months=tenure,
        )

        resp["stage"] = "SALES"
        resp["worker_called"] = "SALES_AGENT"
        resp["worker_payload"] = {
            "customer_profile": payload.customer_profile or {},
            "loan_request": {
                "loan_amount": loan_amount,
                "tenure_months": tenure,
            },
            "pricing": {
                "base_rate": base_rate,
                "personalized_rate": personalized_rate,
                "emi": emi,
            },
        }
        resp["message_to_user"] = (
            f"Based on your profile, a personalized rate of {personalized_rate}% "
            f"is available for a loan amount of ₹{loan_amount:,.0f} over {tenure} months. "
            f"Your estimated EMI is ₹{emi:,.0f}. "
            "Shall we proceed with verification?"
        )
        resp["state_updates"] = {
            "stage": "VERIFICATION",
            "loan_amount": loan_amount,
            "tenure": tenure,
            "personalized_rate": personalized_rate,
            "emi": emi,
        }
        resp["action"] = "continue"

    # --- Stage: VERIFICATION ---
    elif stage == "VERIFICATION":
        # Example: if event says KYC completed (stub for real KYC system)
        kyc_done = payload.event == "kyc_verified" or state.kyc_verified

        resp["stage"] = "VERIFICATION"
        resp["worker_called"] = "VERIFICATION_AGENT"
        resp["worker_payload"] = {
            "customer_id": (payload.customer_profile or {}).get("customer_id"),
            "event": payload.event,
        }

        if kyc_done:
            resp["message_to_user"] = (
                "Your KYC has been successfully verified. "
                "Next, please upload your latest salary slip if your requested "
                "amount is above your pre-approved limit."
            )
            resp["state_updates"] = {"stage": "UNDERWRITING", "kyc_verified": True}
            resp["action"] = "request_upload"
        else:
            resp["message_to_user"] = (
                "Please complete KYC verification to proceed with your loan application."
            )
            resp["state_updates"] = {"stage": "VERIFICATION"}
            resp["action"] = "continue"

    # --- Stage: UNDERWRITING ---
    elif stage == "UNDERWRITING":
        # If user has just uploaded salary slip
        if payload.event == "document_uploaded" and payload.uploaded_document_type == "salary_slip":
            # Backend should trigger salary slip OCR / parsing asynchronously
            resp["stage"] = "UNDERWRITING"
            resp["worker_called"] = "UNDERWRITING_AGENT"
            resp["worker_payload"] = {
                "action": "process_salary_slip",
                "state": state.dict(),
            }
            resp["message_to_user"] = (
                "Received your salary slip. Analysing your income details for underwriting."
            )
            resp["state_updates"] = {"stage": "UNDERWRITING"}
            resp["action"] = "process_salary_slip"
        else:
            # Run deterministic underwriting rules from available state
            loan_amount = state.loan_amount or 0.0
            pre_approved_limit = state.pre_approved_limit
            credit_score = state.credit_score
            monthly_income = (state.crm_data or {}).get("monthly_income")
            emi = state.emi

            explainability = run_underwriting_rules(
                credit_score=credit_score,
                loan_amount=loan_amount,
                pre_approved_limit=pre_approved_limit,
                monthly_income=monthly_income,
                proposed_emi=emi,
            )

            decision = explainability.get("decision")

            resp["stage"] = "UNDERWRITING"
            resp["worker_called"] = "UNDERWRITING_AGENT"
            resp["worker_payload"] = {
                "loan_amount": loan_amount,
                "emi": emi,
                "credit_score": credit_score,
                "pre_approved_limit": pre_approved_limit,
                "monthly_income": monthly_income,
            }
            resp["state_updates"] = {
                "stage": "SANCTION" if decision == "approved" else "UNDERWRITING",
                "explainability": explainability,
            }

            if decision == "approved":
                resp["message_to_user"] = (
                    "Your loan is approved based on your credit profile and income. "
                    "Generating your sanction details now."
                )
                resp["action"] = "continue"
            else:
                resp["message_to_user"] = (
                    "We are unable to approve your loan as per the current policy rules. "
                    "You can review the detailed reasons in the explainability section."
                )
                resp["action"] = "end"

    # --- Stage: SANCTION ---
    elif stage == "SANCTION":
        # Placeholder sanction letter generation; actual PDF generation is handled downstream.
        loan_amount = state.loan_amount or 0.0
        tenure = state.tenure or 0
        rate = state.personalized_rate or 0.0
        emi = state.emi or 0.0

        sanction_number = (state.sanction_data or {}).get("sanction_number") or "TEMP-SANCTION-0001"
        pdf_url = (state.sanction_data or {}).get("pdf_url") or "https://example.com/sanction/TEMP-SANCTION-0001.pdf"

        sanction_data = {
            "sanction_number": sanction_number,
            "loan_amount": loan_amount,
            "tenure_months": tenure,
            "rate_percent": rate,
            "emi": emi,
            "processing_fee": round(0.01 * loan_amount, 2),  # 1% example
            "validity_days": 7,
            "pdf_url": pdf_url,
        }

        resp["stage"] = "SANCTION"
        resp["worker_called"] = "SANCTION_LETTER_AGENT"
        resp["worker_payload"] = {
            "sanction_data": sanction_data,
            "customer_profile": payload.customer_profile or {},
        }
        resp["state_updates"] = {
            "stage": "GAMIFICATION",
            "sanction_data": sanction_data,
        }
        resp["message_to_user"] = (
            "Your loan has been sanctioned. "
            f"Sanction number {sanction_number}. "
            f"Loan amount ₹{loan_amount:,.0f}, tenure {tenure} months at {rate}% "
            f"with an estimated EMI of ₹{emi:,.0f}. "
            "You can download your sanction letter from the provided link."
        )
        resp["action"] = "continue"

    # --- Stage: GAMIFICATION ---
    elif stage == "GAMIFICATION":
        # Basic gamification initialization
        gamification_state = {
            "points_awarded": 200,
            "tier": "Bronze",
            "challenges": [
                "Pay first 6 EMIs on time",
                "Refer 2 friends",
                "Improve credit score by 50+ points",
            ],
        }

        resp["stage"] = "GAMIFICATION"
        resp["worker_called"] = "GAMIFICATION_ENGINE"
        resp["worker_payload"] = {
            "gamification_state": gamification_state,
            "customer_id": (payload.customer_profile or {}).get("customer_id"),
        }
        resp["state_updates"] = {
            "stage": "ECOSYSTEM_OFFERS",
            "gamification": gamification_state,
        }
        resp["message_to_user"] = (
            "Congratulations! You have been awarded 200 starting reward points "
            "and unlocked Bronze tier. Complete challenges like paying 6 EMIs on time "
            "and referrals to level up."
        )
        resp["action"] = "continue"

    # --- Stage: ECOSYSTEM_OFFERS ---
    elif stage == "ECOSYSTEM_OFFERS":
        resp["stage"] = "ECOSYSTEM_OFFERS"
        resp["worker_called"] = "ECOSYSTEM_OFFER_ENGINE"
        resp["worker_payload"] = {
            "customer_profile": payload.customer_profile or {},
            "loan_state": state.dict(),
        }
        resp["state_updates"] = {
            "stage": "ECOSYSTEM_OFFERS",
        }
        resp["message_to_user"] = (
            "Your personal loan journey is complete. "
            "Based on your profile, you may also be eligible for exclusive Tata Capital offers "
            "like credit cards, insurance, or investment products."
        )
        resp["action"] = "end"

    else:
        # Fallback: unknown stage - request human handoff
        resp["stage"] = stage
        resp["worker_called"] = "NONE"
        resp["message_to_user"] = (
            "Your case requires assistance from a human loan specialist."
        )
        resp["action"] = "human_handoff"
        resp["fallback_needed"] = True

    # Finalize message using GPT-5.1-Codex-Max (Preview) when available
    refined_message, model_version = maybe_llm_rewrite(
        message=resp["message_to_user"], state=state
    )
    resp["message_to_user"] = refined_message
    resp["model_version"] = model_version

    return OrchestratorResponse(**resp)


@app.post("/uploadSalarySlip")
async def upload_salary_slip(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Minimal upload handler. Validates PDF up to ~5MB and returns a stub file_id.
    In production, store securely (S3/GCS) and trigger OCR pipeline.
    """

    if file.content_type not in {"application/pdf"}:
        return {"success": False, "message": "Only PDF files are accepted"}

    # FastAPI UploadFile spools to disk; enforce size guard if available
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        return {"success": False, "message": "File too large (max 5MB)"}

    file_id = f"salary_{hash(file.filename) % 10_000_000}"

    return {
        "success": True,
        "message": "Salary slip received",
        "file_id": file_id,
    }
