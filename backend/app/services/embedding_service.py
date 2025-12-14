"""Sentence-Transformers based embedding service.

Provides local text embeddings for search, scoring, and analytics.
Falls back to a deterministic hash-based embedding if the model or
library is unavailable so the rest of the system still functions.
"""
from __future__ import annotations

import hashlib
from typing import List, Optional

from app.config.settings import get_settings

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None) -> None:
        settings = get_settings()
        self._model_name = model_name or settings.embeddings_model_name
        # Use a broad runtime type here to avoid issues when the
        # sentence_transformers library is not installed.
        self._model: Optional[object] = None

        if SentenceTransformer is not None:
            try:  # pragma: no cover - heavy model load
                self._model = SentenceTransformer(self._model_name)
            except Exception as e:  # pragma: no cover
                print(f"EmbeddingService: failed to load model {self._model_name}: {e}")
                self._model = None

    @property
    def available(self) -> bool:
        return self._model is not None

    def embed_text(self, text: str) -> List[float]:
        """Return a single embedding vector for the given text.

        If the Sentence-Transformers model is not available, this uses a
        deterministic SHA-256 based fallback, matching the behavior of the
        previous VectorService implementation.
        """
        if not text:
            return []

        if self._model is not None:
            try:  # pragma: no cover - external model
                vec = self._model.encode(text, normalize_embeddings=True)
                return [float(x) for x in vec]
            except Exception as e:  # pragma: no cover
                print(f"EmbeddingService: encode error: {e}")

        # Fallback: simple 8-dim hash embedding (previous behavior)
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round(b / 255, 4) for b in digest[:8]]
