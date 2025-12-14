"""Audio synthesis and speech-to-text via Google Cloud Speech."""
from __future__ import annotations

import io
from typing import Dict

from google.cloud import speech_v1p1beta1 as speech

from app.config.gcp_auth import gcp_auth


class AudioService:
    def __init__(self) -> None:
        # Lazily create the Speech client; it will use either the
        # service account loaded by GCPAuthManager or default
        # GOOGLE_APPLICATION_CREDENTIALS env if configured.
        if not gcp_auth.is_authenticated:
            # We allow running without real STT; in that case, fall
            # back to a simple placeholder so the app still works.
            self._client: speech.SpeechClient | None = None
        else:
            self._client = speech.SpeechClient.from_service_account_info(
                gcp_auth.service_account  # type: ignore[arg-type]
            )

    def synthesize(self, text: str, voice: str = "neobank_en") -> Dict[str, str]:
        # TTS is still a placeholder in this project.
        return {"voice": voice, "text": text, "url": "/audio/fake-tts.wav"}

    def transcribe(self, audio_bytes: bytes) -> Dict[str, str]:
        """Transcribe audio using Google Cloud Speech-to-Text.

        If Google credentials are not configured, we return a simple
        placeholder transcript instead of raising, so the rest of the
        flow keeps working.
        """

        # No configured client: keep old behaviour.
        if not self._client:
            return {"transcript": "Transcribed audio", "language": "en"}

        try:
            audio = speech.RecognitionAudio(content=audio_bytes)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="en-IN",
                enable_automatic_punctuation=True,
            )

            response = self._client.recognize(config=config, audio=audio)

            transcript_text = "".join(
                result.alternatives[0].transcript
                for result in response.results
                if result.alternatives
            ).strip()

            if not transcript_text:
                transcript_text = "Transcribed audio"

            return {"transcript": transcript_text, "language": "en"}
        except Exception as exc:  # pragma: no cover - defensive
            # If Google returns a 4xx/5xx (e.g. API disabled, bad quota),
            # don't break the app – just fall back to a generic transcript.
            print(f"⚠️  Google STT failed, falling back to placeholder: {exc}")
            return {"transcript": "Transcribed audio", "language": "en"}
