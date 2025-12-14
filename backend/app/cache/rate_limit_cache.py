from __future__ import annotations

from typing import Optional
from app.config.redis_config import redis_client

PREFIX = "rl:"

def increment(key: str, ttl: int = 60) -> int:
    full = PREFIX + key
    pipe = redis_client.pipeline()
    pipe.incr(full)
    pipe.expire(full, ttl)
    count, _ = pipe.execute()
    return int(count)
