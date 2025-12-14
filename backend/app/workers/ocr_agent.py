"""OCR worker that extracts salary details from uploads.

Currently uses a Tesseract-based OCR service to extract raw text from
the uploaded salary slip image and then applies simple heuristics to
estimate salary details. This can be refined over time.
"""
from __future__ import annotations

import re
from typing import Optional

from app.schemas.ocr import OCRResult
from app.services.ocr_service import OcrService


class OcrAgent:
    def __init__(self) -> None:
        self._ocr = OcrService()

    def extract_salary_slip(self, *, file_id: str, file_name: str, file_bytes: bytes) -> OCRResult:
        text = self._ocr.extract_text(file_bytes)

        # Very naive heuristic extraction; in production this should be
        # replaced with template or ML-based parsing.
        gross_salary: Optional[float] = None
        net_salary: Optional[float] = None
        employer: Optional[str] = None
        month: Optional[str] = None

        # Try to pick the largest number that looks like a salary
        numbers = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]{3,}", text)] if text else []
        if numbers:
            gross_salary = max(numbers)
            net_salary = gross_salary  # best-effort; real logic can refine this

        # Very rough employer detection: first line of text
        if text:
            first_line = text.splitlines()[0].strip()
            if first_line:
                employer = first_line

        status = "processed" if text else "failed"
        confidence = 0.6 if text else 0.0

        return OCRResult(
            status=status,
            file_id=file_id,
            gross_salary=gross_salary,
            net_salary=net_salary,
            employer=employer,
            month=month,
            confidence=confidence,
        )
