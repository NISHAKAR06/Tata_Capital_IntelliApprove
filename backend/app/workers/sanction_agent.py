"""Sanction communication worker."""
from __future__ import annotations

from typing import Dict

from app.config.gemini_client import GeminiClient
from app.config.settings import get_settings


class SanctionAgent:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = GeminiClient(model=settings.gemini_model_flash)

    def format_summary(self, sanction_payload: Dict[str, object]) -> str:
        if not self._client.available:
            return "Sanction letter is ready. Please download it from the Documents section."
        prompt = "Create a celebratory but compliant sanction summary under 80 words."
        return self._client.generate(prompt, str(sanction_payload), max_tokens=160) or "Sanction ready."
