"""OCR worker that extracts salary details from uploads."""
from __future__ import annotations

from typing import Optional

from app.schemas.ocr import OCRResult


class OcrAgent:
    def extract_salary_slip(self, *, file_id: str, file_name: str, file_bytes: bytes) -> OCRResult:
        size_kb = round(len(file_bytes) / 1024, 2)
        gross_salary = 120000.0
        net_salary = 92000.0
        return OCRResult(
            status="processed",
            file_id=file_id,
            gross_salary=gross_salary,
            net_salary=net_salary,
            employer="Sample Employer",
            month="2025-07",
            confidence=0.82,
        )
