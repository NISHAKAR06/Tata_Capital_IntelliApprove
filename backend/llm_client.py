"""Compatibility shim for older code expecting `llm_client`.

Provides `LLMClient` with the same interface used by `backend/main.py`:
- property `available`
- method `generate(system_prompt: str, user_message: str, max_tokens: int)`
- property `model_version`

Internally delegates to `app.config.ollama_client.OllamaClient` so we can swap
LLM configuration without changing business logic.
"""
from __future__ import annotations

from typing import Optional

from app.config.ollama_client import OllamaClient


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._client = OllamaClient(api_key=api_key, model=model)

    @property
    def available(self) -> bool:  # pragma: no cover - thin wrapper
        return self._client.available

    @property
    def model_version(self) -> Optional[str]:  # pragma: no cover - thin wrapper
        return self._client.model_version

    def generate(self, *, system_prompt: str, user_message: str, max_tokens: int = 256) -> Optional[str]:
        return self._client.generate(system_prompt=system_prompt, user_prompt=user_message, max_tokens=max_tokens)
