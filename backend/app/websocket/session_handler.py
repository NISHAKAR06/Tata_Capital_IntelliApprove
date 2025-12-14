from __future__ import annotations

from typing import Dict, Any

class SessionHandler:
    """Minimal in-memory session store placeholder."""
    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._sessions.setdefault(session_id, {})

    def set(self, session_id: str, key: str, value: Any) -> None:
        self.get(session_id)[key] = value
