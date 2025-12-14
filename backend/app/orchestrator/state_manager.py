"""State management for conversations: fetch, update, persist.

This implementation uses Redis as the backing store so the full loan
and sanction pipeline state survives process restarts instead of being
kept only in memory.
"""

from typing import Optional

from app.cache.redis_client import redis_client
from app.schemas.conversation_state import OrchestratorState


class StateManager:
    """State store for conversation pipelines (Redis with in-memory fallback).

    If Redis is unavailable (for example in local dev on Windows without a
    Redis server), we fall back to an in-process dict so the chatbot still
    maintains conversation stage and context instead of restarting from the
    greeting on every message.
    """

    _KEY_PREFIX = "conv_state:"
    _fallback_store: dict[str, OrchestratorState] = {}

    @classmethod
    def _key(cls, conversation_id: str) -> str:
        return f"{cls._KEY_PREFIX}{conversation_id}"

    @classmethod
    def get_state(cls, conversation_id: str) -> Optional[OrchestratorState]:
        """Fetch conversation state from Redis or fallback store."""
        try:
            raw = redis_client.get(cls._key(conversation_id))
        except Exception:
            # Redis not available – use in-memory fallback.
            return cls._fallback_store.get(conversation_id)

        if not raw:
            return cls._fallback_store.get(conversation_id)

        try:
            # Pydantic v2 helper to load from JSON string.
            return OrchestratorState.model_validate_json(raw)
        except Exception:
            # Corrupt data – treat as no state in Redis, but we might still
            # have a usable copy in the fallback store.
            return cls._fallback_store.get(conversation_id)

    @classmethod
    def upsert_state(cls, state: OrchestratorState) -> None:
        """Update or insert conversation state into Redis and fallback."""
        if not state.conversation_id:
            return

        try:
            payload = state.model_dump_json()
            redis_client.set(cls._key(state.conversation_id), payload)
        except Exception:
            # Redis failed – rely on in-memory fallback only.
            pass

        # Always keep an in-memory copy for the current process.
        cls._fallback_store[state.conversation_id] = state

    @classmethod
    def delete_state(cls, conversation_id: str) -> None:
        """Delete conversation state from Redis and fallback."""
        try:
            redis_client.delete(cls._key(conversation_id))
        except Exception:
            pass

        cls._fallback_store.pop(conversation_id, None)
