from datetime import datetime
import logging
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logger = logging.getLogger("credit_bureau_server")
logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="Tata Capital Credit Bureau Mock Server",
    version="1.0",
    description="Mock Credit Bureau API simulating CIBIL for Tata Capital BFSI Chatbot",
)


class CreditCheckRequest(BaseModel):
    pan_number: str


# ============================================================================
# IN-MEMORY CREDIT DATABASE (DUMMY DATA)
# ============================================================================

CREDIT_DATABASE: Dict[str, Dict[str, Any]] = {
    "OPQR51267M": {
        "pan_number": "OPQR51267M",
        "customer_name": "Deepika Malhotra",
        "credit_score": 760,
        "score_range": "GOOD",
        "last_updated": "2025-12-14",
        "existing_loans": [
            {
                "loan_id": "LOAN009",
                "loan_type": "BUSINESS_LOAN",
                "outstanding_amount": 750000,
                "monthly_emi": 18000,
                "status": "ACTIVE",
                "tenure_completed": 2,
                "tenure_remaining": 4,
                "disbursement_date": "2023-06-15",
                "due_date": "2027-06-15",
                "last_payment_date": "2025-12-01",
                "days_past_due": 0,
            }
        ],
        "credit_cards": [
            {
                "card_type": "VISA",
                "card_last_4_digits": "1234",
                "utilization_percent": 40,
                "credit_limit": 250000,
                "outstanding_balance": 100000,
                "status": "ACTIVE",
                "days_since_last_payment": 6,
                "minimum_payment_due": 3000,
            }
        ],
        "payment_defaults": 0,
        "payment_defaults_last_24_months": 0,
        "enquiries_last_6_months": 2,
        "enquiries_last_12_months": 3,
        "debt_to_income_ratio": 16.36,
        "last_default_date": None,
        "default_settlement_amount": 0,
    },
    "STUV61278N": {
        "pan_number": "STUV61278N",
        "customer_name": "Sanjay Verma",
        "credit_score": 710,
        "score_range": "GOOD",
        "last_updated": "2025-12-11",
        "existing_loans": [
            {
                "loan_id": "LOAN010",
                "loan_type": "PERSONAL_LOAN",
                "outstanding_amount": 400000,
                "monthly_emi": 11000,
                "status": "ACTIVE",
                "tenure_completed": 1,
                "tenure_remaining": 3,
                "disbursement_date": "2024-12-15",
                "due_date": "2027-12-15",
                "last_payment_date": "2025-12-02",
                "days_past_due": 0,
            }
        ],
        "credit_cards": [
            {
                "card_type": "VISA",
                "card_last_4_digits": "7890",
                "utilization_percent": 50,
                "credit_limit": 150000,
                "outstanding_balance": 75000,
                "status": "ACTIVE",
                "days_since_last_payment": 8,
                "minimum_payment_due": 2250,
            }
        ],
        "payment_defaults": 0,
        "payment_defaults_last_24_months": 0,
        "enquiries_last_6_months": 1,
        "enquiries_last_12_months": 2,
        "debt_to_income_ratio": 31.43,
        "last_default_date": None,
        "default_settlement_amount": 0,
    },
    "WXYZ71289O": {
        "pan_number": "WXYZ71289O",
        "customer_name": "Anjali Reddy",
        "credit_score": 740,
        "score_range": "GOOD",
        "last_updated": "2025-12-13",
        "existing_loans": [
            {
                "loan_id": "LOAN011",
                "loan_type": "HOME_LOAN",
                "outstanding_amount": 2000000,
                "monthly_emi": 20000,
                "status": "ACTIVE",
                "tenure_completed": 4,
                "tenure_remaining": 16,
                "disbursement_date": "2021-12-15",
                "due_date": "2037-12-15",
                "last_payment_date": "2025-12-01",
                "days_past_due": 0,
            }
        ],
        "credit_cards": [
            {
                "card_type": "MASTERCARD",
                "card_last_4_digits": "4567",
                "utilization_percent": 30,
                "credit_limit": 200000,
                "outstanding_balance": 60000,
                "status": "ACTIVE",
                "days_since_last_payment": 7,
                "minimum_payment_due": 1800,
            }
        ],
        "payment_defaults": 0,
        "payment_defaults_last_24_months": 0,
        "enquiries_last_6_months": 0,
        "enquiries_last_12_months": 1,
        "debt_to_income_ratio": 22.73,
        "last_default_date": None,
        "default_settlement_amount": 0,
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_credit_tier(credit_score: int) -> str:
    """Determine credit tier based on CIBIL credit score."""

    if credit_score >= 800:
        return "EXCELLENT"
    elif credit_score >= 750:
        return "VERY_GOOD"
    elif credit_score >= 700:
        return "GOOD"
    elif credit_score >= 650:
        return "FAIR"
    else:
        return "POOR"


def calculate_total_debt(customer_data: dict) -> dict:
    """Calculate total debt obligations from loans and credit cards."""

    total_loan_emi = sum(loan["monthly_emi"] for loan in customer_data["existing_loans"])
    total_cc_balance = sum(cc["outstanding_balance"] for cc in customer_data["credit_cards"])
    cc_minimum_payment = sum(cc["minimum_payment_due"] for cc in customer_data["credit_cards"])

    return {
        "total_loan_emi": total_loan_emi,
        "total_cc_balance": total_cc_balance,
        "cc_minimum_payment": cc_minimum_payment,
        "total_monthly_obligation": total_loan_emi + cc_minimum_payment,
    }


def get_underwriting_recommendation(dti: float, credit_score: int, defaults: int) -> tuple[str, str, int]:
    """Generate underwriting recommendation based on credit metrics."""

    if dti <= 50 and credit_score >= 700 and defaults == 0:
        return (
            "INSTANT_APPROVE",
            f"Low DTI ({dti:.1f}%), Strong credit score ({credit_score}), No defaults",
            95,
        )
    elif dti <= 100 and credit_score >= 650 and defaults == 0:
        return (
            "NEEDS_SALARY_VERIFICATION",
            f"Moderate DTI ({dti:.1f}%), Acceptable credit score ({credit_score})",
            70,
        )
    elif dti <= 100 and credit_score >= 650:
        return (
            "MANUAL_REVIEW",
            f"DTI {dti:.1f}%, Credit score {credit_score}, but has defaults",
            50,
        )
    else:
        reasons = []
        if dti > 100:
            reasons.append(f"High DTI ({dti:.1f}%)")
        if credit_score < 650:
            reasons.append(f"Low credit score ({credit_score})")
        if defaults > 0:
            reasons.append(f"Payment defaults ({defaults})")
        return ("REJECT", f"Unable to approve: {', '.join(reasons)}", 20)


# ============================================================================
# ROOT & HEALTH CHECK ENDPOINTS
# ============================================================================


@app.get("/")
async def root() -> dict:
    """Root endpoint with service information."""

    return {
        "service": "Credit Bureau Mock Server",
        "version": "1.0",
        "status": "running",
        "port": 8002,
        "description": "Mock Credit Bureau API simulating CIBIL for Tata Capital BFSI Chatbot",
        "endpoints_available": {
            "health": "/api/credit-bureau/health",
            "check_credit": "/api/credit-bureau/check-credit (POST)",
            "credit_score": "/api/credit-bureau/credit-score/{pan_number} (GET)",
            "debt_obligations": "/api/credit-bureau/debt-obligations/{pan_number} (GET)",
            "payment_history": "/api/credit-bureau/payment-history/{pan_number} (GET)",
            "dti_ratio": "/api/credit-bureau/dti-ratio/{pan_number} (GET)",
            "detailed_report": "/api/credit-bureau/detailed-report (POST)",
            "all_records": "/api/credit-bureau/all-records (GET)",
            "statistics": "/api/credit-bureau/statistics (GET)",
            "test_data": "/api/credit-bureau/test-data/{pan_number} (GET)",
        },
    }


@app.get("/api/credit-bureau/health")
async def health_check() -> dict:
    """Health check endpoint to verify server is running."""

    return {
        "status": "healthy",
        "service": "Credit Bureau Server",
        "port": 8002,
        "timestamp": datetime.now().isoformat(),
        "database_records": len(CREDIT_DATABASE),
        "uptime": "Running",
    }


# ============================================================================
# PRIMARY ENDPOINTS - CREDIT CHECK
# ============================================================================


@app.post("/api/credit-bureau/check-credit")
async def check_credit(request: CreditCheckRequest):
    """Main endpoint: Check complete credit profile of customer."""

    logger.info("Credit check request for PAN: %s", request.pan_number)

    if request.pan_number not in CREDIT_DATABASE:
        logger.warning("PAN not found: %s", request.pan_number)
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {request.pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[request.pan_number]
    debt_info = calculate_total_debt(customer_data)
    credit_tier = get_credit_tier(customer_data["credit_score"])

    logger.info("Credit check successful for %s", customer_data["customer_name"])

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "pan_number": customer_data["pan_number"],
            "customer_name": customer_data["customer_name"],
            "credit_score": customer_data["credit_score"],
            "credit_tier": credit_tier,
            "score_range": customer_data["score_range"],
            "last_updated": customer_data["last_updated"],
            "existing_loans": customer_data["existing_loans"],
            "credit_cards": customer_data["credit_cards"],
            "payment_profile": {
                "total_defaults": customer_data["payment_defaults"],
                "defaults_last_24_months": customer_data["payment_defaults_last_24_months"],
                "enquiries_last_6_months": customer_data["enquiries_last_6_months"],
                "enquiries_last_12_months": customer_data["enquiries_last_12_months"],
                "last_default_date": customer_data["last_default_date"],
            },
            "debt_analysis": debt_info,
            "debt_to_income_ratio": customer_data["debt_to_income_ratio"],
        },
    }


@app.get("/api/credit-bureau/credit-score/{pan_number}")
async def get_credit_score(pan_number: str):
    """Quick endpoint: Get only credit score information."""

    logger.info("Credit score request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    credit_tier = get_credit_tier(customer_data["credit_score"])

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "credit_score": customer_data["credit_score"],
            "credit_tier": credit_tier,
            "score_range": customer_data["score_range"],
            "last_updated": customer_data["last_updated"],
            "score_interpretation": {
                "EXCELLENT (800+)": "Exceptional creditworthiness",
                "VERY_GOOD (750-799)": "Very strong credit profile",
                "GOOD (700-749)": "Acceptable credit profile",
                "FAIR (650-699)": "Below average credit profile",
                "POOR (<650)": "High credit risk",
            },
        },
    }


# ============================================================================
# DEBT & OBLIGATION ENDPOINTS
# ============================================================================


@app.get("/api/credit-bureau/debt-obligations/{pan_number}")
async def get_debt_obligations(pan_number: str):
    """Get total debt obligations (loans + credit cards)."""

    logger.info("Debt obligations request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    debt_info = calculate_total_debt(customer_data)

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "debt_summary": {
                "existing_loans_count": len(
                    [l for l in customer_data["existing_loans"] if l["status"] == "ACTIVE"]
                ),
                "total_loan_emi": debt_info["total_loan_emi"],
                "credit_cards_count": len(
                    [cc for cc in customer_data["credit_cards"] if cc["status"] == "ACTIVE"]
                ),
                "total_cc_outstanding": debt_info["total_cc_balance"],
                "cc_minimum_payment": debt_info["cc_minimum_payment"],
                "total_monthly_obligation": debt_info["total_monthly_obligation"],
            },
            "existing_loans": [
                {
                    "loan_id": loan["loan_id"],
                    "loan_type": loan["loan_type"],
                    "outstanding_amount": loan["outstanding_amount"],
                    "monthly_emi": loan["monthly_emi"],
                    "status": loan["status"],
                    "tenure_remaining": loan["tenure_remaining"],
                }
                for loan in customer_data["existing_loans"]
            ],
            "credit_cards": [
                {
                    "card_type": cc["card_type"],
                    "card_last_4_digits": cc["card_last_4_digits"],
                    "outstanding_balance": cc["outstanding_balance"],
                    "minimum_payment_due": cc["minimum_payment_due"],
                    "utilization_percent": cc["utilization_percent"],
                }
                for cc in customer_data["credit_cards"]
            ],
        },
    }


# ============================================================================
# PAYMENT HISTORY ENDPOINTS
# ============================================================================


@app.get("/api/credit-bureau/payment-history/{pan_number}")
async def get_payment_history(pan_number: str):
    """Get payment history and default information."""

    logger.info("Payment history request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "payment_discipline": {
                "total_defaults_lifetime": customer_data["payment_defaults"],
                "defaults_last_24_months": customer_data["payment_defaults_last_24_months"],
                "last_default_date": customer_data["last_default_date"],
                "default_settlement_amount": customer_data["default_settlement_amount"],
                "payment_status": "EXCELLENT"
                if customer_data["payment_defaults"] == 0
                else "AT_RISK",
            },
            "enquiry_history": {
                "enquiries_last_6_months": customer_data["enquiries_last_6_months"],
                "enquiries_last_12_months": customer_data["enquiries_last_12_months"],
                "enquiry_status": "LOW"
                if customer_data["enquiries_last_6_months"] <= 2
                else "HIGH",
            },
            "recent_loans": [
                {
                    "loan_id": loan["loan_id"],
                    "loan_type": loan["loan_type"],
                    "status": loan["status"],
                    "last_payment_date": loan["last_payment_date"],
                    "days_past_due": loan["days_past_due"],
                    "payment_status": "ON_TIME"
                    if loan["days_past_due"] == 0
                    else "OVERDUE",
                }
                for loan in customer_data["existing_loans"]
            ],
        },
    }


# ============================================================================
# DTI RATIO ENDPOINT - KEY UNDERWRITING METRIC
# ============================================================================


@app.get("/api/credit-bureau/dti-ratio/{pan_number}")
async def get_dti_ratio(pan_number: str):
    """Get debt-to-income ratio and approval recommendation."""

    logger.info("DTI ratio request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    dti = customer_data["debt_to_income_ratio"]

    if dti <= 50:
        dti_status = "EXCELLENT"
        approval_status = "INSTANT_APPROVE"
        recommendation = "Low DTI - High approval probability (>90%)"
    elif dti <= 100:
        dti_status = "ACCEPTABLE"
        approval_status = "NEEDS_SALARY_VERIFICATION"
        recommendation = "Moderate DTI - Needs income verification"
    else:
        dti_status = "HIGH_RISK"
        approval_status = "REJECT"
        recommendation = "High DTI - Low approval probability (<30%)"

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "debt_to_income_ratio": dti,
            "dti_percentage": f"{dti:.2f}%",
            "dti_status": dti_status,
            "approval_status": approval_status,
            "approval_recommendation": recommendation,
            "dti_benchmarks": {
                "excellent": "0-30%",
                "good": "30-50%",
                "acceptable": "50-100%",
                "high_risk": ">100%",
            },
            "current_dti_category": (
                "EXCELLENT"
                if dti <= 30
                else "GOOD"
                if dti <= 50
                else "ACCEPTABLE"
                if dti <= 100
                else "HIGH_RISK"
            ),
        },
    }


# ============================================================================
# DETAILED REPORT ENDPOINT - FOR UNDERWRITING
# ============================================================================


@app.post("/api/credit-bureau/detailed-report")
async def get_detailed_report(request: CreditCheckRequest):
    """Get comprehensive credit report with underwriting analysis."""

    logger.info("Detailed report request for PAN: %s", request.pan_number)

    if request.pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {request.pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[request.pan_number]
    debt_info = calculate_total_debt(customer_data)
    credit_tier = get_credit_tier(customer_data["credit_score"])
    dti = customer_data["debt_to_income_ratio"]

    recommendation, reasoning, confidence = get_underwriting_recommendation(
        dti,
        customer_data["credit_score"],
        customer_data["payment_defaults"],
    )

    avg_utilization = (
        sum(cc["utilization_percent"] for cc in customer_data["credit_cards"])
        / len(customer_data["credit_cards"])
        if customer_data["credit_cards"]
        else 0
    )

    approval_factors: Dict[str, Dict[str, Any]] = {
        "credit_score": {
            "value": customer_data["credit_score"],
            "weight": "HIGH",
            "status": "POSITIVE"
            if customer_data["credit_score"] >= 700
            else "NEGATIVE",
            "score": customer_data["credit_score"],
        },
        "dti_ratio": {
            "value": f"{dti:.2f}%",
            "weight": "HIGH",
            "status": "POSITIVE" if dti <= 50 else "FAIR" if dti <= 100 else "NEGATIVE",
            "score": dti,
        },
        "payment_defaults": {
            "value": customer_data["payment_defaults"],
            "weight": "HIGH",
            "status": "POSITIVE"
            if customer_data["payment_defaults"] == 0
            else "NEGATIVE",
            "score": customer_data["payment_defaults"],
        },
        "enquiries_last_6m": {
            "value": customer_data["enquiries_last_6_months"],
            "weight": "MEDIUM",
            "status": "POSITIVE"
            if customer_data["enquiries_last_6_months"] <= 2
            else "NEGATIVE",
            "score": customer_data["enquiries_last_6_months"],
        },
        "credit_card_utilization": {
            "value": f"{avg_utilization:.1f}%",
            "weight": "MEDIUM",
            "status": "POSITIVE" if avg_utilization <= 50 else "NEGATIVE",
            "score": avg_utilization,
        },
    }

    positive_factors = sum(
        1 for f in approval_factors.values() if f["status"] in {"POSITIVE", "FAIR"}
    )
    total_factors = len(approval_factors)

    logger.info(
        "Detailed report generated for %s - Recommendation: %s",
        customer_data["customer_name"],
        recommendation,
    )

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "pan_number": request.pan_number,
            "customer_name": customer_data["customer_name"],
            "credit_profile": {
                "credit_score": customer_data["credit_score"],
                "credit_tier": credit_tier,
                "score_range": customer_data["score_range"],
                "tier_interpretation": {
                    "EXCELLENT": "Exceptional creditworthiness - Lowest risk",
                    "VERY_GOOD": "Very strong credit profile - Low risk",
                    "GOOD": "Acceptable credit profile - Moderate risk",
                    "FAIR": "Below average credit profile - Higher risk",
                    "POOR": "High credit risk - Highest risk",
                }[credit_tier],
            },
            "debt_analysis": {
                "total_active_loans": len(
                    [l for l in customer_data["existing_loans"] if l["status"] == "ACTIVE"]
                ),
                "total_loan_emi": debt_info["total_loan_emi"],
                "active_credit_cards": len(
                    [cc for cc in customer_data["credit_cards"] if cc["status"] == "ACTIVE"]
                ),
                "total_cc_balance": debt_info["total_cc_balance"],
                "total_monthly_obligation": debt_info["total_monthly_obligation"],
                "debt_to_income_ratio": dti,
            },
            "payment_history": {
                "total_defaults": customer_data["payment_defaults"],
                "defaults_last_24_months": customer_data["payment_defaults_last_24_months"],
                "last_default_date": customer_data["last_default_date"],
                "default_settlement_amount": customer_data["default_settlement_amount"],
                "credit_enquiries_6m": customer_data["enquiries_last_6_months"],
                "credit_enquiries_12m": customer_data["enquiries_last_12_months"],
            },
            "approval_factors_assessment": {
                "factors": approval_factors,
                "positive_factors": f"{positive_factors}/{total_factors}",
                "overall_score": f"{(positive_factors / total_factors) * 100:.1f}%",
            },
            "underwriting_decision": {
                "recommendation": recommendation,
                "confidence_score": f"{confidence}%",
                "reasoning": reasoning,
            },
            "loan_details": {
                "existing_loans": customer_data["existing_loans"],
                "credit_cards": customer_data["credit_cards"],
            },
        },
    }


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.get("/api/credit-bureau/all-records")
async def get_all_credit_records() -> dict:
    """Get all credit records (for testing and demo purposes)."""

    logger.info("All records request")

    records = []
    for pan, data in CREDIT_DATABASE.items():
        records.append(
            {
                "pan_number": pan,
                "customer_name": data["customer_name"],
                "credit_score": data["credit_score"],
                "credit_tier": get_credit_tier(data["credit_score"]),
                "dti_ratio": data["debt_to_income_ratio"],
                "defaults": data["payment_defaults"],
                "status": "ACTIVE" if data["payment_defaults"] == 0 else "AT_RISK",
            }
        )

    return {
        "status": "success",
        "total_records": len(records),
        "data": records,
    }


@app.get("/api/credit-bureau/customer-summary/{pan_number}")
async def get_customer_summary(pan_number: str):
    """Get quick summary of customer credit profile."""

    logger.info("Customer summary request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
                "data": None,
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    debt_info = calculate_total_debt(customer_data)

    return {
        "status": "success",
        "data": {
            "summary": {
                "name": customer_data["customer_name"],
                "pan": pan_number,
                "credit_score": customer_data["credit_score"],
                "credit_tier": get_credit_tier(customer_data["credit_score"]),
                "risk_level": "LOW"
                if customer_data["credit_score"] >= 700
                else "MEDIUM"
                if customer_data["credit_score"] >= 650
                else "HIGH",
            },
            "finances": {
                "active_loans": len(
                    [l for l in customer_data["existing_loans"] if l["status"] == "ACTIVE"]
                ),
                "total_loan_emi": debt_info["total_loan_emi"],
                "credit_cards": len(
                    [cc for cc in customer_data["credit_cards"] if cc["status"] == "ACTIVE"]
                ),
                "total_cc_balance": debt_info["total_cc_balance"],
                "dti_ratio": customer_data["debt_to_income_ratio"],
            },
            "payment_record": {
                "defaults": customer_data["payment_defaults"],
                "last_default": customer_data["last_default_date"],
                "enquiries_6m": customer_data["enquiries_last_6_months"],
            },
        },
    }


@app.get("/api/credit-bureau/statistics")
async def get_database_statistics() -> dict:
    """Get statistics about the credit database."""

    logger.info("Statistics request")

    all_scores = [data["credit_score"] for data in CREDIT_DATABASE.values()]
    all_dti = [data["debt_to_income_ratio"] for data in CREDIT_DATABASE.values()]

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "total_customers": len(CREDIT_DATABASE),
            "credit_score_stats": {
                "average": round(sum(all_scores) / len(all_scores), 2),
                "min": min(all_scores),
                "max": max(all_scores),
                "median": sorted(all_scores)[len(all_scores) // 2],
            },
            "dti_stats": {
                "average": round(sum(all_dti) / len(all_dti), 2),
                "min": round(min(all_dti), 2),
                "max": round(max(all_dti), 2),
            },
            "credit_tier_distribution": {
                "EXCELLENT": len(
                    [d for d in CREDIT_DATABASE.values() if get_credit_tier(d["credit_score"]) == "EXCELLENT"]
                ),
                "VERY_GOOD": len(
                    [d for d in CREDIT_DATABASE.values() if get_credit_tier(d["credit_score"]) == "VERY_GOOD"]
                ),
                "GOOD": len(
                    [d for d in CREDIT_DATABASE.values() if get_credit_tier(d["credit_score"]) == "GOOD"]
                ),
                "FAIR": len(
                    [d for d in CREDIT_DATABASE.values() if get_credit_tier(d["credit_score"]) == "FAIR"]
                ),
                "POOR": len(
                    [d for d in CREDIT_DATABASE.values() if get_credit_tier(d["credit_score"]) == "POOR"]
                ),
            },
            "defaults_summary": {
                "customers_with_defaults": len(
                    [d for d in CREDIT_DATABASE.values() if d["payment_defaults"] > 0]
                ),
                "customers_without_defaults": len(
                    [d for d in CREDIT_DATABASE.values() if d["payment_defaults"] == 0]
                ),
            },
            "approval_likelihood": {
                "instant_approve": len(
                    [
                        d
                        for d in CREDIT_DATABASE.values()
                        if d["debt_to_income_ratio"] <= 50 and d["credit_score"] >= 700
                    ]
                ),
                "needs_verification": len(
                    [
                        d
                        for d in CREDIT_DATABASE.values()
                        if 50 < d["debt_to_income_ratio"] <= 100 and d["credit_score"] >= 650
                    ]
                ),
                "likely_reject": len(
                    [
                        d
                        for d in CREDIT_DATABASE.values()
                        if d["debt_to_income_ratio"] > 100 or d["credit_score"] < 650
                    ]
                ),
            },
        },
    }


@app.get("/api/credit-bureau/test-data/{pan_number}")
async def get_test_customer_data(pan_number: str):
    """Get test customer data for development/testing scenarios."""

    logger.info("Test data request for PAN: %s", pan_number)

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"Test data not found for PAN {pan_number}",
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    credit_tier = get_credit_tier(customer_data["credit_score"])
    dti = customer_data["debt_to_income_ratio"]

    if (
        dti <= 50
        and customer_data["credit_score"] >= 700
        and customer_data["payment_defaults"] == 0
    ):
        scenario = "INSTANT_APPROVAL"
        description = (
            "Low DTI and excellent credit score - Should get instant approval"
        )
    elif (
        dti <= 100
        and customer_data["credit_score"] >= 650
        and customer_data["payment_defaults"] == 0
    ):
        scenario = "SALARY_VERIFICATION_REQUIRED"
        description = (
            "Moderate DTI and acceptable credit - Needs salary slip verification"
        )
    elif (
        dti <= 100
        and customer_data["credit_score"] >= 650
        and customer_data["payment_defaults"] > 0
    ):
        scenario = "MANUAL_REVIEW_REQUIRED"
        description = "Has payment defaults - Needs manual underwriting review"
    else:
        scenario = "LIKELY_REJECTION"
        description = "High DTI or poor credit - Low approval probability"

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "test_scenario": scenario,
            "scenario_description": description,
            "key_metrics": {
                "credit_score": customer_data["credit_score"],
                "credit_tier": credit_tier,
                "dti_ratio": dti,
                "defaults": customer_data["payment_defaults"],
                "enquiries_6m": customer_data["enquiries_last_6_months"],
            },
            "expected_flow": {
                "INSTANT_APPROVAL": (
                    "Customer -> Master Agent -> Salary Verification (skip) -> "
                    "Underwriting (auto-approve) -> Sanction Letter"
                ),
                "SALARY_VERIFICATION_REQUIRED": (
                    "Customer -> Master Agent -> Salary Verification (required) -> "
                    "Underwriting (approve if verified) -> Sanction Letter"
                ),
                "MANUAL_REVIEW_REQUIRED": (
                    "Customer -> Master Agent -> Salary Verification -> "
                    "Underwriting (manual review) -> Decision"
                ),
                "LIKELY_REJECTION": (
                    "Customer -> Master Agent -> Salary Verification -> "
                    "Underwriting (reject) -> Alternative offers"
                ),
            }[scenario],
        },
    }


# ============================================================================
# APPROVAL CALCULATOR ENDPOINT
# ============================================================================


@app.post("/api/credit-bureau/approval-calculator")
async def approval_calculator(request: Dict[str, Any]):
    """Calculate approval probability for a new loan request."""

    pan_number = request.get("pan_number")

    if pan_number not in CREDIT_DATABASE:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No credit record found for PAN {pan_number}",
            },
        )

    customer_data = CREDIT_DATABASE[pan_number]
    dti = customer_data["debt_to_income_ratio"]
    credit_score = customer_data["credit_score"]
    defaults = customer_data["payment_defaults"]

    approval_prob = 100

    if credit_score >= 800:
        approval_prob += 15
    elif credit_score >= 750:
        approval_prob += 10
    elif credit_score >= 700:
        approval_prob += 5
    elif credit_score >= 650:
        approval_prob -= 5
    else:
        approval_prob -= 30

    if dti <= 30:
        approval_prob += 15
    elif dti <= 50:
        approval_prob += 5
    elif dti <= 100:
        approval_prob -= 10
    else:
        approval_prob -= 40

    if defaults == 0:
        approval_prob += 10
    elif defaults == 1:
        approval_prob -= 20
    else:
        approval_prob -= 50

    approval_prob = max(10, min(99, approval_prob))

    recommendation, reasoning, _ = get_underwriting_recommendation(
        dti, credit_score, defaults
    )

    return {
        "status": "success",
        "data": {
            "pan_number": pan_number,
            "customer_name": customer_data["customer_name"],
            "approval_probability": f"{approval_prob}%",
            "approval_recommendation": recommendation,
            "reasoning": reasoning,
            "credit_score_impact": "POSITIVE"
            if credit_score >= 700
            else "NEGATIVE",
            "dti_impact": "POSITIVE" if dti <= 50 else "NEGATIVE",
            "payment_history_impact": "POSITIVE"
            if defaults == 0
            else "NEGATIVE",
        },
    }


# ============================================================================
# ERROR HANDLING
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    """Custom HTTP exception handler."""

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
    """General exception handler."""

    logger.error("Unexpected error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================


@app.on_event("startup")
async def startup_event() -> None:
    """Log server startup."""

    logger.info("%s", "=" * 80)
    logger.info("CREDIT BUREAU MOCK SERVER STARTED")
    logger.info("%s", "=" * 80)
    logger.info("Port: 8002")
    logger.info("Total customers in database: %d", len(CREDIT_DATABASE))
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log server shutdown."""

    logger.info("%s", "=" * 80)
    logger.info("CREDIT BUREAU MOCK SERVER SHUTTING DOWN")
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


# ============================================================================
# MAIN - RUN SERVER
# ============================================================================


if __name__ == "__main__":
    print("=" * 80)
    print("CREDIT BUREAU MOCK SERVER")
    print("=" * 80)
    print("Starting Credit Bureau Server on http://0.0.0.0:8002")
    print("API Documentation: http://localhost:8002/docs")
    print("ReDoc Documentation: http://localhost:8002/redoc")
    print(f"Total customers: {len(CREDIT_DATABASE)}")
    print("=" * 80)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        reload=False,
    )
