"""LLM client wrapper for Google Gemini.

This wraps the official `google-generativeai` SDK behind a simple interface used
throughout the app, so callers don't depend on any specific provider details.
"""
from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - external SDK import
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None  # type: ignore

from .settings import get_settings


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        # Default to flash / pro model names from settings when not explicitly provided
        self._model = model or settings.gemini_model_flash

        if genai and self._api_key:
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(self._model)
        else:  # pragma: no cover - disabled when SDK or key missing
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    @property
    def model_version(self) -> Optional[str]:
        return self._model if self.available else None

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate a completion from Gemini.

        Returns `None` on any error so callers can gracefully fall back.
        """
        if not self.available:
            print("GeminiClient: Not available (client is None)")
            return None

        try:  # pragma: no cover - external API call
            prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.3,
                },
            )
            text = getattr(response, "text", None) or (response.candidates[0].content.parts[0].text if response.candidates else None)
            return text.strip() if text else None
        except Exception as e:
            print(f"GeminiClient Error: {e}")
            # Check if it's a safety filter issue (has 'response' attribute)
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
                print(f"GeminiClient Feedback: {e.response.prompt_feedback}")
            return None
