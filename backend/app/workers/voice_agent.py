"""Voice agent bridging text and speech."""
from __future__ import annotations

from typing import Dict

from app.services.audio_service import AudioService


class VoiceAgent:
    def __init__(self) -> None:
        self._audio = AudioService()

    def to_speech(self, text: str) -> Dict[str, str]:
        return self._audio.synthesize(text)

    def to_text(self, audio_bytes: bytes) -> Dict[str, str]:
        return self._audio.transcribe(audio_bytes)
