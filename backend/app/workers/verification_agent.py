"""Verification worker using Ollama."""
from __future__ import annotations

from typing import Dict

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_verification_system_prompt


class VerificationAgent:
    def __init__(self) -> None:
        settings = get_settings()
        # Use per-agent Ollama model
        model_name = settings.ollama_model_verification or settings.ollama_model_default
        self._client = OllamaClient(model=model_name)
        self._base_system_prompt = get_verification_system_prompt()

    def summarize_checks(self, context: Dict[str, str]) -> str:
        if not self._client.available:
            return "OTP validated. We have verified your KYC details successfully."
        system_prompt = self._base_system_prompt or "You are a KYC verification agent. Summarize verification status in under 60 words."
        msg = str(context)
        return self._client.generate(system_prompt, msg, max_tokens=120) or "Verification completed."
