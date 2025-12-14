"""Vector service using local embeddings and Weaviate.

This wraps the EmbeddingService (Sentence-Transformers) for generating
embeddings and optionally a Weaviate client for vector search and storage.

Existing callers can continue using ``embed_text`` while new code can
use ``index_text`` and ``query_similar`` for semantic search.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config.settings import get_settings
from app.services.embedding_service import EmbeddingService

try:  # pragma: no cover - optional dependency
    import weaviate  # type: ignore
    from weaviate.classes.init import Auth  # type: ignore
except ImportError:  # pragma: no cover
    weaviate = None  # type: ignore
    Auth = None  # type: ignore


class VectorService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._embedder = EmbeddingService()

        self._client = None
        if weaviate is not None:
            try:  # pragma: no cover - external client
                auth = None
                if self._settings.weaviate_api_key:
                    auth = Auth.api_key(self._settings.weaviate_api_key)

                self._client = weaviate.Client(
                    self._settings.weaviate_url,
                    auth_client_secret=auth,
                )
            except Exception as e:  # pragma: no cover
                print(f"VectorService: failed to init Weaviate client: {e}")
                self._client = None

    # --- Embeddings ---

    def embed_text(self, text: str) -> List[float]:
        """Return an embedding for the given text.

        This is used by the ScoringEngine and other internal components.
        """
        return self._embedder.embed_text(text)

    # --- Weaviate helpers ---

    @property
    def weaviate_available(self) -> bool:
        return self._client is not None

    def index_text(
        self,
        *,
        class_name: str,
        text: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Index a text document in Weaviate.

        ``class_name`` should refer to an existing Weaviate class. The
        embedding is computed locally and passed via ``vector`` so that
        Weaviate can store it without its own embedding module.
        """
        if not self.weaviate_available:
            return None

        vector = self.embed_text(text)
        data = properties or {}
        data.setdefault("text", text)

        try:  # pragma: no cover - external call
            uuid = self._client.collections.get(class_name).data.insert(
                properties=data,
                vector=vector,
            )
            return str(uuid)
        except Exception as e:
            print(f"VectorService.index_text error: {e}")
            return None

    def query_similar(
        self,
        *,
        class_name: str,
        text: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query Weaviate for documents similar to the given text.

        Returns a list of objects with their properties and distances.
        If Weaviate is not available, an empty list is returned.
        """
        if not self.weaviate_available:
            return []

        vector = self.embed_text(text)

        try:  # pragma: no cover - external call
            coll = self._client.collections.get(class_name)
            res = coll.query.near_vector(
                near_vector=vector,
                limit=limit,
                return_metadata=["distance"],
            )
            results: List[Dict[str, Any]] = []
            for o in res.objects:
                results.append(
                    {
                        "uuid": str(o.uuid),
                        "properties": o.properties,
                        "distance": getattr(o.metadata, "distance", None),
                    }
                )
            return results
        except Exception as e:
            print(f"VectorService.query_similar error: {e}")
            return []

