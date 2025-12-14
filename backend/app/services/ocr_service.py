"""Tesseract-based OCR service for salary slips and documents.

Uses the local Tesseract binary via pytesseract to extract raw text
from image files. The higher-level OcrAgent is responsible for mapping
this text into structured salary fields.
"""
from __future__ import annotations

from io import BytesIO
from typing import Optional

import pytesseract  # type: ignore
from PIL import Image  # type: ignore


class OcrService:
    def __init__(self, tesseract_cmd: Optional[str] = None) -> None:
        # Optionally allow overriding the Tesseract binary path (useful on Windows)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, file_bytes: bytes) -> str:
        """Run OCR on the given image bytes and return plain text.

        Supports common formats like PNG and JPEG. For PDFs, convert pages
        to images before calling this service.
        """
        if not file_bytes:
            return ""

        try:  # pragma: no cover - external binary
            with BytesIO(file_bytes) as buf:
                image = Image.open(buf)
                text = pytesseract.image_to_string(image)
                return text.strip()
        except Exception as e:
            print(f"OcrService.extract_text error: {e}")
            return ""
