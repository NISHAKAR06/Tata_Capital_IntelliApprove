"""Embeddings helper."""
from __future__ import annotations

import hashlib
from typing import List


class VectorService:
    def embed_text(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # Return deterministic 8-dim embedding
        return [round(b / 255, 4) for b in digest[:8]]
