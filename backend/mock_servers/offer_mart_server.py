from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OfferRequest(BaseModel):
    """Request to generate loan offer"""

    pan_number: str
    monthly_income: float
    credit_score: int
    existing_debt: float
    desired_amount: float
    desired_tenure: Optional[int] = 48


class EMICalculationRequest(BaseModel):
    """Request to calculate EMI"""

    principal: float
    annual_rate: float
    tenure_months: int


app = FastAPI(
    title="Offer Mart Mock Server",
    version="1.0",
    description="Mock Offer Mart API for generating personalized loan offers",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


INTEREST_RATE_TIERS: Dict[str, Dict[str, Any]] = {
    "EXCELLENT": {"min": 8.5, "max": 10.5, "typical": 9.5, "credit_range": "800+"},
    "VERY_GOOD": {"min": 10.5, "max": 12.5, "typical": 11.5, "credit_range": "750-799"},
    "GOOD": {"min": 10.5, "max": 14.5, "typical": 12.5, "credit_range": "700-749"},
    "FAIR": {"min": 13.5, "max": 16.5, "typical": 15.0, "credit_range": "650-699"},
    "POOR": {"min": 16.5, "max": 18.0, "typical": 17.25, "credit_range": "Below 650"},
}


LOAN_AMOUNT_MULTIPLIERS: Dict[str, int] = {
    "EXCELLENT": 20,
    "VERY_GOOD": 18,
    "GOOD": 15,
    "FAIR": 12,
    "POOR": 8,
}


TENURE_OPTIONS: List[int] = [12, 24, 36, 48, 60]
MIN_LOAN_AMOUNT = 50000
MAX_LOAN_AMOUNT = 2500000
MIN_TENURE = 12
MAX_TENURE = 60
MAX_EMI_PERCENTAGE = 50


PROCESSING_FEE_STRUCTURE: Dict[str, float] = {
    "EXCELLENT": 1.0,
    "VERY_GOOD": 1.0,
    "GOOD": 1.5,
    "FAIR": 2.0,
    "POOR": 2.5,
}


def get_credit_tier(credit_score: int) -> str:
    if credit_score >= 800:
        return "EXCELLENT"
    if credit_score >= 750:
        return "VERY_GOOD"
    if credit_score >= 700:
        return "GOOD"
    if credit_score >= 650:
        return "FAIR"
    return "POOR"


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    if annual_rate == 0:
        return round(principal / tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1

    try:
        emi = numerator / denominator
        return round(emi, 2)
    except ZeroDivisionError:
        return 0.0


def get_interest_rate_for_customer(credit_score: int, dti_ratio: float) -> float:
    credit_tier = get_credit_tier(credit_score)
    rate_range = INTEREST_RATE_TIERS[credit_tier]

    min_rate = rate_range["min"]
    max_rate = rate_range["max"]

    if dti_ratio < 20:
        interest_rate = min_rate
    elif dti_ratio < 35:
        interest_rate = (min_rate + max_rate) / 2 - (max_rate - min_rate) / 4
    elif dti_ratio < 50:
        interest_rate = (min_rate + max_rate) / 2
    elif dti_ratio < 100:
        interest_rate = (min_rate + max_rate) / 2 + (max_rate - min_rate) / 4
    else:
        interest_rate = max_rate

    interest_rate = round(interest_rate * 2) / 2
    interest_rate = max(min_rate, min(interest_rate, max_rate))
    return interest_rate


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "Offer Mart Mock Server",
        "version": "1.0",
        "status": "running",
        "port": 8003,
        "description": "Mock Offer Mart API for generating personalized loan offers",
        "endpoints_available": {
            "health": "/api/offer-mart/health",
            "check_eligibility": "/api/offer-mart/check-eligibility (POST)",
            "generate_offers": "/api/offer-mart/generate-offers (POST)",
            "interest_rates": "/api/offer-mart/interest-rates (GET)",
            "loan_multipliers": "/api/offer-mart/loan-multipliers (GET)",
            "calculate_emi": "/api/offer-mart/calculate-emi (POST)",
            "offer_details": "/api/offer-mart/offer-details (POST)",
        },
    }


@app.get("/api/offer-mart/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "Offer Mart Server",
        "port": 8003,
        "timestamp": datetime.now().isoformat(),
        "tenure_options": TENURE_OPTIONS,
        "min_loan": MIN_LOAN_AMOUNT,
        "max_loan": MAX_LOAN_AMOUNT,
    }


@app.post("/api/offer-mart/check-eligibility")
async def check_eligibility(request: OfferRequest):
    logger.info("Eligibility check request for PAN: %s", request.pan_number)

    try:
        if request.monthly_income <= 0:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Monthly income must be positive"},
            )

        if request.credit_score < 300 or request.credit_score > 900:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Credit score must be between 300-900",
                },
            )

        credit_tier = get_credit_tier(request.credit_score)
        max_loan_multiplier = LOAN_AMOUNT_MULTIPLIERS[credit_tier]
        eligible_amount = request.monthly_income * max_loan_multiplier

        final_eligible_amount = min(
            eligible_amount,
            MAX_LOAN_AMOUNT,
            request.desired_amount * 1.2,
        )

        proposed_emi = calculate_emi(final_eligible_amount, 12.0, 48)
        total_monthly_obligation = request.existing_debt + proposed_emi
        dti_ratio = (total_monthly_obligation / request.monthly_income) * 100

        interest_rate = get_interest_rate_for_customer(request.credit_score, dti_ratio)

        processing_fee_percent = PROCESSING_FEE_STRUCTURE[credit_tier]
        processing_fee = final_eligible_amount * (processing_fee_percent / 100)

        if dti_ratio <= 50 and request.credit_score >= 700:
            approval_likelihood = "VERY_HIGH"
            recommendation = "High approval probability - Instant approval expected"
        elif dti_ratio <= 100 and request.credit_score >= 650:
            approval_likelihood = "HIGH"
            recommendation = (
                "Good approval probability - Salary verification may be needed"
            )
        elif dti_ratio <= 100:
            approval_likelihood = "MODERATE"
            recommendation = "Moderate approval probability - Manual review required"
        else:
            approval_likelihood = "LOW"
            recommendation = (
                "Low approval probability - Consider reducing loan amount"
            )

        logger.info("Eligibility check completed for %s - Tier: %s", request.pan_number, credit_tier)

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "pan_number": request.pan_number,
                "credit_tier": credit_tier,
                "credit_score": request.credit_score,
                "eligible_amount": round(final_eligible_amount, 2),
                "interest_rate": interest_rate,
                "processing_fee_percent": processing_fee_percent,
                "processing_fee_amount": round(processing_fee, 2),
                "dti_ratio": round(dti_ratio, 2),
                "approval_likelihood": approval_likelihood,
                "recommendation": recommendation,
                "loan_limits": {
                    "min": MIN_LOAN_AMOUNT,
                    "max": MAX_LOAN_AMOUNT,
                    "eligible": round(final_eligible_amount, 2),
                },
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in eligibility check: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during eligibility check",
            },
        )


@app.post("/api/offer-mart/generate-offers")
async def generate_offers(request: OfferRequest):
    logger.info("Offer generation request for PAN: %s", request.pan_number)

    try:
        eligibility_response = await check_eligibility(request)

        if isinstance(eligibility_response, JSONResponse):
            return eligibility_response

        if eligibility_response.get("status") != "success":
            return eligibility_response

        eligibility_data = eligibility_response["data"]
        eligible_amount = eligibility_data["eligible_amount"]
        interest_rate = eligibility_data["interest_rate"]
        processing_fee_percent = eligibility_data["processing_fee_percent"]
        dti_ratio = eligibility_data["dti_ratio"]

        credit_tier = get_credit_tier(request.credit_score)

        offers: List[Dict[str, Any]] = []

        for tenure in TENURE_OPTIONS:
            emi = calculate_emi(eligible_amount, interest_rate, tenure)

            if emi > (request.monthly_income * MAX_EMI_PERCENTAGE / 100):
                continue

            processing_fee = eligible_amount * (processing_fee_percent / 100)
            net_disbursal = eligible_amount - processing_fee
            total_interest = (emi * tenure) - eligible_amount
            total_amount_payable = emi * tenure

            recommended = tenure == request.desired_tenure or tenure == 48

            offers.append(
                {
                    "offer_id": f"OFFER_{request.pan_number}_{tenure}M",
                    "tenure_months": tenure,
                    "monthly_emi": round(emi, 2),
                    "total_interest": round(total_interest, 2),
                    "processing_fee": round(processing_fee, 2),
                    "net_disbursal": round(net_disbursal, 2),
                    "total_amount_payable": round(total_amount_payable, 2),
                    "is_recommended": recommended,
                    "validity_days": 30,
                }
            )

        if not offers:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "No suitable offers could be generated with current parameters",
                },
            )

        logger.info("Generated %d offers for %s", len(offers), request.pan_number)

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "pan_number": request.pan_number,
                "credit_tier": credit_tier,
                "credit_score": request.credit_score,
                "eligible_amount": eligible_amount,
                "interest_rate": interest_rate,
                "processing_fee_percent": processing_fee_percent,
                "dti_ratio": round(dti_ratio, 2),
                "offers_count": len(offers),
                "offers": offers,
                "note": "Choose the offer that best fits your repayment capability",
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in offer generation: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during offer generation",
            },
        )


@app.post("/api/offer-mart/calculate-emi")
async def calculate_emi_endpoint(
    request: EMICalculationRequest,
):
    logger.info(
        "EMI calculation request - Principal: %s, Rate: %s%%, Tenure: %sM",
        request.principal,
        request.annual_rate,
        request.tenure_months,
    )

    try:
        if request.principal <= 0:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Principal must be positive"},
            )

        if request.annual_rate < 0 or request.annual_rate > 50:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Interest rate must be between 0-50%",
                },
            )

        if request.tenure_months < MIN_TENURE or request.tenure_months > MAX_TENURE:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Tenure must be between {MIN_TENURE}-{MAX_TENURE} months",
                },
            )

        emi = calculate_emi(request.principal, request.annual_rate, request.tenure_months)
        total_interest = (emi * request.tenure_months) - request.principal
        total_amount_payable = emi * request.tenure_months

        logger.info("EMI calculated: Rs. %s", emi)

        return {
            "status": "success",
            "data": {
                "principal": request.principal,
                "rate_of_interest": request.annual_rate,
                "tenure_months": request.tenure_months,
                "monthly_emi": emi,
                "total_interest": round(total_interest, 2),
                "total_amount_payable": round(total_amount_payable, 2),
                "breakdown": {
                    "principal_repayment": f"{(request.principal / total_amount_payable) * 100:.1f}%",
                    "interest_component": f"{(total_interest / total_amount_payable) * 100:.1f}%",
                },
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in EMI calculation: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during EMI calculation",
            },
        )


@app.get("/api/offer-mart/interest-rates")
async def get_interest_rates() -> Dict[str, Any]:
    logger.info("Interest rates information requested")

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "interest_rate_tiers": INTEREST_RATE_TIERS,
            "tenure_options": TENURE_OPTIONS,
            "processing_fee_range": {
                "min": min(PROCESSING_FEE_STRUCTURE.values()),
                "max": max(PROCESSING_FEE_STRUCTURE.values()),
            },
            "loan_limits": {
                "min_amount": MIN_LOAN_AMOUNT,
                "max_amount": MAX_LOAN_AMOUNT,
                "min_tenure": MIN_TENURE,
                "max_tenure": MAX_TENURE,
            },
            "last_updated": datetime.now().isoformat(),
        },
    }


@app.get("/api/offer-mart/loan-multipliers")
async def get_loan_multipliers() -> Dict[str, Any]:
    logger.info("Loan multipliers information requested")

    return {
        "status": "success",
        "data": {
            "multipliers": LOAN_AMOUNT_MULTIPLIERS,
            "description": "Loan Amount = Monthly Income × Multiplier",
            "note": "Actual eligible amount depends on credit score and DTI ratio",
        },
    }


@app.get("/api/offer-mart/processing-fees")
async def get_processing_fees() -> Dict[str, Any]:
    logger.info("Processing fees information requested")

    return {
        "status": "success",
        "data": {
            "processing_fee_structure": PROCESSING_FEE_STRUCTURE,
            "note": "Processing fee is deducted from loan amount before disbursement",
        },
    }


@app.post("/api/offer-mart/offer-details")
async def get_offer_details(request: Dict[str, Any]):
    logger.info("Offer details requested for offer ID: %s", request.get("offer_id"))

    try:
        loan_amount = request.get("loan_amount")
        interest_rate = request.get("interest_rate")
        tenure_months = request.get("tenure_months")

        emi = calculate_emi(loan_amount, interest_rate, tenure_months)
        total_interest = (emi * tenure_months) - loan_amount

        if interest_rate <= 10.5:
            credit_tier = "EXCELLENT"
            processing_fee_percent = PROCESSING_FEE_STRUCTURE["EXCELLENT"]
        elif interest_rate <= 12.5:
            credit_tier = "VERY_GOOD"
            processing_fee_percent = PROCESSING_FEE_STRUCTURE["VERY_GOOD"]
        elif interest_rate <= 14.5:
            credit_tier = "GOOD"
            processing_fee_percent = PROCESSING_FEE_STRUCTURE["GOOD"]
        elif interest_rate <= 16.5:
            credit_tier = "FAIR"
            processing_fee_percent = PROCESSING_FEE_STRUCTURE["FAIR"]
        else:
            credit_tier = "POOR"
            processing_fee_percent = PROCESSING_FEE_STRUCTURE["POOR"]

        processing_fee = loan_amount * (processing_fee_percent / 100)
        net_disbursal = loan_amount - processing_fee

        payment_schedule: List[Dict[str, Any]] = []
        remaining_principal = loan_amount

        for month in range(1, 7):
            interest_payment = remaining_principal * (interest_rate / 12 / 100)
            principal_payment = emi - interest_payment
            remaining_principal -= principal_payment

            payment_schedule.append(
                {
                    "month": month,
                    "emi": round(emi, 2),
                    "principal": round(principal_payment, 2),
                    "interest": round(interest_payment, 2),
                    "remaining_balance": round(max(0, remaining_principal), 2),
                }
            )

        return {
            "status": "success",
            "data": {
                "offer_id": request.get("offer_id"),
                "pan_number": request.get("pan_number"),
                "credit_tier": credit_tier,
                "loan_details": {
                    "loan_amount": loan_amount,
                    "interest_rate": f"{interest_rate}% p.a.",
                    "tenure_months": tenure_months,
                    "monthly_emi": round(emi, 2),
                },
                "cost_breakdown": {
                    "principal": loan_amount,
                    "total_interest": round(total_interest, 2),
                    "processing_fee": round(processing_fee, 2),
                    "total_amount_payable": round(emi * tenure_months, 2),
                },
                "disbursement_details": {
                    "loan_sanctioned": loan_amount,
                    "processing_fee_deducted": round(processing_fee, 2),
                    "net_amount_disbursed": round(net_disbursal, 2),
                },
                "repayment_summary": {
                    "total_emis": tenure_months,
                    "monthly_emi": round(emi, 2),
                    "total_interest_paid": round(total_interest, 2),
                    "total_repayment": round(emi * tenure_months, 2),
                },
                "first_6_months_payment_schedule": payment_schedule,
                "offer_validity": {
                    "valid_from": datetime.now().isoformat(),
                    "valid_till": (datetime.now() + timedelta(days=30)).isoformat(),
                    "validity_days": 30,
                },
                "terms_and_conditions": {
                    "prepayment_penalty": "No",
                    "insurance_included": "Yes - Personal Accident Insurance",
                    "processing_fee_refundable": "No",
                    "offer_transferable": "No",
                },
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in offer details: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error getting offer details",
            },
        )


@app.post("/api/offer-mart/compare-offers")
async def compare_offers(request: Dict[str, Any]):
    logger.info("Offer comparison request for PAN: %s", request.get("pan_number"))

    try:
        offers_request = OfferRequest(
            pan_number=request.get("pan_number"),
            monthly_income=request.get("monthly_income"),
            credit_score=request.get("credit_score"),
            existing_debt=request.get("existing_debt"),
            desired_amount=request.get("desired_amount"),
        )

        offers_response = await generate_offers(offers_request)

        if isinstance(offers_response, JSONResponse):
            return offers_response

        if offers_response.get("status") != "success":
            return offers_response

        offers_data = offers_response["data"]
        offers = offers_data["offers"]

        comparison: Dict[str, Any] = {
            "status": "success",
            "data": {
                "pan_number": request.get("pan_number"),
                "loan_amount": offers_data["eligible_amount"],
                "interest_rate": offers_data["interest_rate"],
                "comparison_table": [],
            },
        }

        base_interest = offers[0]["total_interest"] if offers else 0

        for offer in offers:
            comparison["data"]["comparison_table"].append(
                {
                    "tenure": f"{offer['tenure_months']} months",
                    "monthly_emi": f"Rs. {offer['monthly_emi']:,.2f}",
                    "total_interest": f"Rs. {offer['total_interest']:,.2f}",
                    "total_repayment": f"Rs. {offer['total_amount_payable']:,.2f}",
                    "cost_difference_vs_12m": (
                        "Base"
                        if offer["tenure_months"] == 12
                        else f"+Rs. {offer['total_interest'] - base_interest:,.2f}"
                    ),
                    "recommended": "03" if offer["is_recommended"] else "",
                }
            )

        return comparison
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in offer comparison: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during offer comparison",
            },
        )


@app.post("/api/offer-mart/validate-loan-request")
async def validate_loan_request(request: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Loan request validation")

    loan_amount = request.get("loan_amount")
    tenure = request.get("tenure")
    monthly_income = request.get("monthly_income")

    errors: List[str] = []
    warnings: List[str] = []

    if loan_amount < MIN_LOAN_AMOUNT:
        errors.append(f"Minimum loan amount is Rs. {MIN_LOAN_AMOUNT}")

    if loan_amount > MAX_LOAN_AMOUNT:
        errors.append(f"Maximum loan amount is Rs. {MAX_LOAN_AMOUNT}")

    if tenure < MIN_TENURE or tenure > MAX_TENURE:
        errors.append(f"Tenure must be between {MIN_TENURE}-{MAX_TENURE} months")

    if monthly_income and loan_amount:
        multiplier = loan_amount / monthly_income
        if multiplier > 20:
            warnings.append(f"Loan is {multiplier:.1f}x monthly income - May be high")

    if monthly_income and loan_amount and tenure:
        estimated_emi = calculate_emi(loan_amount, 12.0, tenure)
        emi_percentage = (estimated_emi / monthly_income) * 100

        if emi_percentage > 50:
            errors.append(f"EMI exceeds 50% of monthly income ({emi_percentage:.1f}%)")
        elif emi_percentage > 40:
            warnings.append(
                f"EMI is high ({emi_percentage:.1f}% of monthly income)"
            )

    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "message": "All validations passed" if not errors else "Please fix the errors",
    }


@app.post("/api/offer-mart/get-best-offer")
async def get_best_offer(request: OfferRequest):
    logger.info("Best offer recommendation for PAN: %s", request.pan_number)

    try:
        offers_response = await generate_offers(request)

        if isinstance(offers_response, JSONResponse):
            return offers_response

        if offers_response.get("status") != "success":
            return offers_response

        offers = offers_response["data"]["offers"]

        if not offers:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No suitable offers available"},
            )

        best_offer: Optional[Dict[str, Any]] = None
        best_score = -1.0

        for offer in offers:
            emi_percentage = (offer["monthly_emi"] / request.monthly_income) * 100
            emi_score = max(0.0, 100.0 - emi_percentage)

            cost_score = max(
                0.0, 100.0 - (offer["total_interest"] / max(offer["monthly_emi"], 1) * 10)
            )

            tenure_middle = 48
            tenure_diff = abs(offer["tenure_months"] - tenure_middle)
            tenure_score = max(0.0, 100.0 - (tenure_diff * 2.0))

            overall_score = (emi_score * 0.4) + (cost_score * 0.4) + (tenure_score * 0.2)

            if overall_score > best_score:
                best_score = overall_score
                best_offer = dict(offer)
                best_offer["score"] = round(overall_score, 2)

        return {
            "status": "success",
            "data": {
                "pan_number": request.pan_number,
                "recommended_offer": best_offer,
                "recommendation_reason": (
                    "This offer provides the best balance between affordable EMI "
                    f"(Rs. {best_offer['monthly_emi']:,.2f}) and total cost "
                    f"(Rs. {best_offer['total_amount_payable']:,.2f})"
                ),
                "all_offers_available": len(offers),
                "note": (
                    "You can also choose other tenure options if this doesn't "
                    "suit your needs"
                ),
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in best offer recommendation: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error getting best offer recommendation",
            },
        )


@app.post("/api/offer-mart/scenario-analysis")
async def scenario_analysis(request: Dict[str, Any]):
    logger.info("Scenario analysis requested")

    try:
        scenarios = request.get("scenarios", [])
        monthly_income = request.get("monthly_income")
        credit_score = request.get("credit_score")
        existing_debt = request.get("existing_debt")

        if not scenarios:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No scenarios provided"},
            )

        analysis: List[Dict[str, Any]] = []

        for scenario in scenarios:
            loan_amount = scenario.get("amount")
            tenure = scenario.get("tenure")

            credit_tier = get_credit_tier(credit_score)
            proposed_emi = calculate_emi(loan_amount, 12.0, tenure)
            total_obligation = existing_debt + proposed_emi
            dti_ratio = (total_obligation / monthly_income) * 100

            interest_rate = get_interest_rate_for_customer(credit_score, dti_ratio)

            emi = calculate_emi(loan_amount, interest_rate, tenure)
            total_interest = (emi * tenure) - loan_amount

            emi_pct = (emi / monthly_income) * 100
            if emi_pct <= 30:
                affordability = "VERY_COMFORTABLE"
            elif emi_pct <= 40:
                affordability = "COMFORTABLE"
            elif emi_pct <= 50:
                affordability = "TIGHT"
            else:
                affordability = "UNAFFORDABLE"

            analysis.append(
                {
                    "loan_amount": loan_amount,
                    "tenure_months": tenure,
                    "monthly_emi": round(emi, 2),
                    "total_interest": round(total_interest, 2),
                    "total_repayment": round(emi * tenure, 2),
                    "dti_ratio": f"{round(dti_ratio, 2)}%",
                    "interest_rate": interest_rate,
                    "affordability": affordability,
                    "emi_percentage_income": f"{round(emi_pct, 2)}%",
                }
            )

        return {
            "status": "success",
            "data": {
                "monthly_income": monthly_income,
                "credit_score": credit_score,
                "credit_tier": credit_tier,
                "scenarios_analyzed": len(analysis),
                "analysis": analysis,
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Error in scenario analysis: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error during scenario analysis",
            },
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.error("Unexpected error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("%s", "=" * 80)
    logger.info("OFFER MART MOCK SERVER STARTED")
    logger.info("%s", "=" * 80)
    logger.info("Port: 8003")
    logger.info("Tenure options: %s", TENURE_OPTIONS)
    logger.info(
        "Loan limits: Rs. %s - Rs. %s",
        f"{MIN_LOAN_AMOUNT:,}",
        f"{MAX_LOAN_AMOUNT:,}",
    )
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("%s", "=" * 80)
    logger.info("OFFER MART MOCK SERVER SHUTTING DOWN")
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print("OFFER MART MOCK SERVER")
    print("=" * 80)
    print("Starting Offer Mart Server on http://0.0.0.0:8003")
    print("API Documentation: http://localhost:8003/docs")
    print("ReDoc Documentation: http://localhost:8003/redoc")
    print(f"Loan Range: Rs. {MIN_LOAN_AMOUNT:,} - Rs. {MAX_LOAN_AMOUNT:,}")
    print(f"Tenure Options: {TENURE_OPTIONS}")
    print("=" * 80)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False,
    )
