"""Sanction communication worker powered by Ollama.

This agent is responsible for:
- Generating a human-readable sanction summary (via LLM when available).
- Creating a local PDF sanction letter on disk and returning its metadata.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_sanction_system_prompt


class SanctionAgent:
    def __init__(self) -> None:
        settings = get_settings()
        # Use per-agent Ollama model when configured, otherwise default
        model_name = settings.ollama_model_sanction or settings.ollama_model_default
        self._client = OllamaClient(model=model_name)
        self._base_system_prompt = get_sanction_system_prompt()

    def generate_letter(self, customer_profile: Dict[str, Any], loan_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple PDF sanction letter and store it locally.

        Returns a dict with sanction_number, file_path and valid_until.
        """

        # Local folder under backend/app/../data/sanctions
        base_dir = Path(__file__).resolve().parents[2] / "data" / "sanctions"
        base_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        customer_id = customer_profile.get("customer_id") or "UNKNOWN"
        sanction_number = f"SL/{now:%Y%m%d}/{customer_id}"
        filename = f"{sanction_number.replace('/', '_')}.pdf"
        file_path = base_dir / filename

        # Basic letter fields
        name = customer_profile.get("name", "Valued Customer")
        address = customer_profile.get("address", "Address on file")
        amount = loan_details.get("amount")
        tenure = loan_details.get("tenure")
        rate = loan_details.get("rate")
        emi = loan_details.get("emi")

        valid_until = (now + timedelta(days=30)).date().isoformat()

        # Create a very simple PDF letter
        c = canvas.Canvas(str(file_path), pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Tata Capital - Personal Loan Sanction Letter")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date: {now.date().isoformat()}")
        y -= 15
        c.drawString(50, y, f"Sanction Letter No: {sanction_number}")
        y -= 30

        c.drawString(50, y, f"To,")
        y -= 15
        c.drawString(50, y, name)
        y -= 15
        c.drawString(50, y, address)
        y -= 30

        c.setFont("Helvetica", 11)
        c.drawString(50, y, "Subject: Sanction of Personal Loan")
        y -= 25

        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Dear Customer,")
        y -= 20

        body_lines = [
            "We are pleased to inform you that your personal loan application has been approved.",
            f"Sanctioned Amount: ₹{amount}" if amount is not None else "Sanctioned Amount: As per approved terms",
            f"Interest Rate: {rate:.2f}% p.a." if isinstance(rate, (int, float)) else "Interest Rate: As per approved schedule",
            f"Tenure: {tenure} months" if tenure is not None else "Tenure: As per approved schedule",
            f"EMI: ₹{int(round(emi))}" if isinstance(emi, (int, float)) else "EMI: As per repayment schedule",
            f"This offer is valid until: {valid_until}.",
            "Funds will be disbursed to your registered bank account post completion of documentation.",
        ]

        for line in body_lines:
            c.drawString(50, y, line)
            y -= 15

        y -= 15
        c.drawString(50, y, "Thank you for choosing Tata Capital.")
        y -= 30
        c.drawString(50, y, "Sincerely,")
        y -= 15
        c.drawString(50, y, "Tata Capital Personal Loans Team")

        c.showPage()
        c.save()

        return {
            "sanction_number": sanction_number,
            "file_path": str(file_path),
            "valid_until": valid_until,
        }

    def format_summary(self, sanction_payload: Dict[str, Any]) -> str:
        """Create a short, celebratory but compliant sanction summary."""

        if not self._client.available:
            return "Your loan has been sanctioned. A copy of the sanction letter has been saved to your account documents."
        system_prompt = self._base_system_prompt or "You are a sanction agent. Create a celebratory but compliant sanction summary under 80 words."
        return self._client.generate(system_prompt, str(sanction_payload), max_tokens=160) or "Sanction ready."
