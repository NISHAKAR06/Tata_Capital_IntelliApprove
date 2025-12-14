"""LLM client wrapper backed by Ollama.

This exposes a simple interface used throughout the app so callers don't
depend on provider details. Under the hood it calls a local Ollama server
over HTTP, using ``OLLAMA_BASE_URL`` and model names passed in by agents
or configured via settings.
"""
from __future__ import annotations

from typing import Optional

import httpx

from .settings import get_settings


class OllamaClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        settings = get_settings()

        # Ollama backend configuration only
        self._ollama_base_url: Optional[str] = settings.ollama_base_url.rstrip("/") if settings.ollama_base_url else None

        # If a model is explicitly passed, treat it as the Ollama model name.
        # Otherwise, fall back to the default configured in settings.
        if model:
            self._ollama_model = model
        else:
            self._ollama_model = settings.ollama_model_default

        # _model is kept for compatibility / introspection
        self._model = self._ollama_model or "ollama-model-not-configured"

    @property
    def available(self) -> bool:
        # Available if we have a model name and base URL configured
        return bool(self._ollama_base_url and self._ollama_model)

    @property
    def model_version(self) -> Optional[str]:
        return self._model if self.available else None

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate a completion from Ollama.

        Returns `None` on any error so callers can gracefully fall back.
        """
        if not self.available:
            print("OllamaClient: Not available (missing base URL or model)")
            return None

        prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
        try:  # pragma: no cover - external API call
            response = httpx.post(
                f"{self._ollama_base_url}/api/generate",
                json={
                    "model": self._ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": max_tokens,
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response")
            return text.strip() if text else None
        except Exception as e:  # pragma: no cover - networking
            print(f"OllamaClient Error: {e}")
            return None
