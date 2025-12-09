"""Audio synthesis and ASR placeholders."""
from __future__ import annotations

from typing import Dict


class AudioService:
    def synthesize(self, text: str, voice: str = "neobank_en") -> Dict[str, str]:
        return {"voice": voice, "text": text, "url": "/audio/fake-tts.wav"}

    def transcribe(self, audio_bytes: bytes) -> Dict[str, str]:
        return {"transcript": "Transcribed audio", "language": "en"}
