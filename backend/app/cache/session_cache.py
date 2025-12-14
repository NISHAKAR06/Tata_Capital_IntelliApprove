from __future__ import annotations

from typing import Any, Dict
from app.cache.redis_client import redis_client

PREFIX = "session:"

def get_state(conversation_id: str) -> Dict[str, Any]:
    data = redis_client.get(PREFIX + conversation_id)
    return {} if not data else {}

def set_state(conversation_id: str, state: Dict[str, Any]) -> None:
    redis_client.set(PREFIX + conversation_id, str(state))
