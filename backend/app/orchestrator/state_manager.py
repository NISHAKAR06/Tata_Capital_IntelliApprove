"""State management for conversations: fetch, update, persist."""
from typing import Optional

from app.schemas.conversation_state import OrchestratorState


class StateManager:
    """In-memory state store (can be swapped for Redis/Postgres)."""

    # TODO: wire to Redis or database for production
    _state_store: dict[str, OrchestratorState] = {}

    @classmethod
    def get_state(cls, conversation_id: str) -> Optional[OrchestratorState]:
        """Fetch conversation state."""
        return cls._state_store.get(conversation_id)

    @classmethod
    def upsert_state(cls, state: OrchestratorState) -> None:
        """Update or insert conversation state."""
        cls._state_store[state.conversation_id] = state

    @classmethod
    def delete_state(cls, conversation_id: str) -> None:
        """Delete conversation state."""
        if conversation_id in cls._state_store:
            del cls._state_store[conversation_id]
