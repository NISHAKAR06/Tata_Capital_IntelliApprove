"""Experimental scoring engine."""
from __future__ import annotations

from typing import Dict

from app.services.vector_service import VectorService


class ScoringEngine:
    def __init__(self) -> None:
        self._vector = VectorService()

    def score_conversation(self, transcript: str) -> Dict[str, float]:
        embedding = self._vector.embed_text(transcript)
        health = round(sum(embedding) / len(embedding), 3) if embedding else 0.0
        return {"engagement": health, "complexity": 1 - health}
