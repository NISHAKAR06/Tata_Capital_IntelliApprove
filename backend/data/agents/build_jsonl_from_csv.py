from __future__ import annotations

import csv
import json
from pathlib import Path

# This file lives at: <repo_root>/backend/data/agents/build_jsonl_from_csv.py
# parents[0] -> backend/data/agents
# parents[1] -> backend/data
# parents[2] -> backend
# parents[3] -> <repo_root>
ROOT = Path(__file__).resolve().parents[3]

DATA_VERIFICATION = ROOT / "dataset_3_verification_agent.csv"
DATA_UNDERWRITING = ROOT / "dataset_4_underwriting_agent.csv"
DATA_SALARY_SLIP = ROOT / "dataset_5_salary_slip_agent.csv"
DATA_SANCTION = ROOT / "dataset_6_sanction_letters.csv"

OUT_DIR = ROOT / "backend" / "data" / "agents"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_verification() -> None:
    if not DATA_VERIFICATION.exists():
        return

    records: list[dict] = []
    with DATA_VERIFICATION.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            customer_id = r.get("customer_id")
            mobile = r.get("registered_mobile")
            email = r.get("email")
            address = r.get("address")
            pan = r.get("pan_number")
            aadhaar_last4 = r.get("aadhaar_last4")
            kyc_verified = r.get("kyc_verified")
            emotion = r.get("detected_emotion")

            instruction = (
                "You are the KYC & contact-details Verification Agent for IntelliApprove. "
                "You only handle checking and confirming mobile number, email, address, PAN and Aadhaar last-4, "
                "and whether KYC is complete or still pending. "
                "Given the structured profile and system flags, you must output if KYC is verified or not, "
                "and reflect the detected customer emotion in a concise way."
            )
            input_text = (
                f"customer_id={customer_id}, mobile={mobile}, email={email}, "
                f"address={address}, pan={pan}, aadhaar_last4={aadhaar_last4}"
            )
            output_text = f"KYC_VERIFIED={kyc_verified}; EMOTION={emotion}."

            records.append(
                {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                }
            )

    out_path = OUT_DIR / "verification" / "train.jsonl"
    _write_jsonl(out_path, records)


def build_underwriting() -> None:
    if not DATA_UNDERWRITING.exists():
        return

    records: list[dict] = []
    with DATA_UNDERWRITING.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            credit_score = r.get("credit_score")
            salary = r.get("monthly_salary")
            existing_emi = r.get("existing_emi")
            loan_amount = r.get("loan_amount_requested")
            pre_approved_limit = r.get("pre_approved_limit")
            expected_emi = r.get("expected_emi")
            ratio = r.get("emi_to_income_ratio")
            salary_slip_required = r.get("salary_slip_required")
            salary_slip_uploaded = r.get("salary_slip_uploaded")
            decision = r.get("final_decision")
            emotion = r.get("detected_emotion")

            instruction = (
                "You are the Underwriting Decision Agent for IntelliApprove. "
                "You take credit score, monthly salary, existing EMIs, requested amount, pre-approved limit, "
                "EMI-to-income ratio, and salary-slip status, and decide whether the loan should be approved or rejected. "
                "Your response should clearly state the decision and briefly mention 2-3 key drivers, "
                "keeping the tone aligned with the detected customer emotion."
            )
            input_text = (
                f"credit_score={credit_score}, monthly_salary={salary}, existing_emi={existing_emi}, "
                f"loan_amount_requested={loan_amount}, pre_approved_limit={pre_approved_limit}, "
                f"expected_emi={expected_emi}, emi_to_income_ratio={ratio}, "
                f"salary_slip_required={salary_slip_required}, salary_slip_uploaded={salary_slip_uploaded}"
            )
            output_text = f"{decision} (emotion={emotion})."

            records.append(
                {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                }
            )

    out_path = OUT_DIR / "underwriting" / "train.jsonl"
    _write_jsonl(out_path, records)


def build_salary_slip() -> None:
    if not DATA_SALARY_SLIP.exists():
        return

    records: list[dict] = []
    with DATA_SALARY_SLIP.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            customer_id = r.get("customer_id")
            salary = r.get("monthly_salary")
            employer = r.get("employer_name")
            uploaded = r.get("salary_slip_uploaded")
            file_type = r.get("file_type")
            status = r.get("verification_status")
            emotion = r.get("detected_emotion")

            instruction = (
                "You are the Salary Slip & Document Verification Agent for IntelliApprove. "
                "Given the uploaded salary slip details such as employer, salary, file type and system status, "
                "decide whether the salary slip should be marked as verified or rejected. "
                "Keep the response short, clearly state the verification status, and reflect the likely customer emotion."
            )
            input_text = (
                f"customer_id={customer_id}, monthly_salary={salary}, employer_name={employer}, "
                f"salary_slip_uploaded={uploaded}, file_type={file_type}"
            )
            output_text = f"VERIFICATION_STATUS={status}; EMOTION={emotion}."

            records.append(
                {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                }
            )

    out_path = OUT_DIR / "salary_slip" / "train.jsonl"
    _write_jsonl(out_path, records)


def build_sanction() -> None:
    if not DATA_SANCTION.exists():
        return

    records: list[dict] = []
    with DATA_SANCTION.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            customer_id = r.get("customer_id")
            amount = r.get("loan_amount_approved")
            rate = r.get("interest_rate")
            tenure = r.get("tenure_months")
            emi = r.get("monthly_emi")
            sanction_date = r.get("sanction_date")
            account_no = r.get("loan_account_number")
            status = r.get("sanction_status")
            emotion = r.get("detected_emotion")

            instruction = (
                "You are the Sanction Communication Agent for IntelliApprove. "
                "You take structured sanction details (approved amount, rate, tenure, EMI, date, account number, status) "
                "and generate a short, clear customer-facing explanation of the sanction outcome. "
                "Always mention amount, rate, tenure, EMI, sanction date, masked account number and status, "
                "and keep the message compliant and neutral while reflecting the detected emotion."
            )
            input_text = (
                f"customer_id={customer_id}, loan_amount_approved={amount}, interest_rate={rate}, "
                f"tenure_months={tenure}, monthly_emi={emi}, sanction_date={sanction_date}, "
                f"loan_account_number={account_no}, sanction_status={status}"
            )
            output_text = (
                "Your loan has been sanctioned. "
                f"Amount ₹{amount} at an interest rate of {rate}% for {tenure} months, "
                f"with an approximate EMI of ₹{emi}. Sanction date {sanction_date}, "
                f"loan account number {account_no}. Status: {status}. "
                f"(customer emotion: {emotion})."
            )

            records.append(
                {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                }
            )

    out_path = OUT_DIR / "sanction" / "train.jsonl"
    _write_jsonl(out_path, records)


def main() -> None:
    build_verification()
    build_underwriting()
    build_salary_slip()
    build_sanction()


if __name__ == "__main__":
    main()
