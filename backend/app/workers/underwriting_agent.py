"""Underwriting agent powered by Gemini Pro."""
from __future__ import annotations

from typing import Dict

from app.config.gemini_client import GeminiClient
from app.config.settings import get_settings


class UnderwritingAgent:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = GeminiClient(model=settings.gemini_model_pro)

    def explain_decision(self, explainability: Dict[str, object]) -> str:
        if not self._client.available:
            summary = explainability.get("summary") if isinstance(explainability, dict) else None
            return summary or "Underwriting completed."
        prompt = "Explain underwriting result in plain English under 80 words."
        return self._client.generate(prompt, str(explainability), max_tokens=200) or "Underwriting completed."
