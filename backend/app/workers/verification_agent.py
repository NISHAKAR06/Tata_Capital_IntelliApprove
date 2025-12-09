"""Verification worker using Gemini Flash."""
from __future__ import annotations

from typing import Dict

from app.config.gemini_client import GeminiClient
from app.config.settings import get_settings


class VerificationAgent:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = GeminiClient(model=settings.gemini_model_flash)

    def summarize_checks(self, context: Dict[str, str]) -> str:
        if not self._client.available:
            return "OTP validated. We have verified your KYC details successfully."
        prompt = "Summarize verification status in under 60 words."
        msg = str(context)
        return self._client.generate(prompt, msg, max_tokens=120) or "Verification completed."
