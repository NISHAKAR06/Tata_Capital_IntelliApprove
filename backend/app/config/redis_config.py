"""Redis configuration shim."""
from __future__ import annotations

import redis
from app.config.settings import get_settings

settings = get_settings()
# Set a reasonable timeout to ensure we connect to the running Redis instance
redis_client = redis.Redis.from_url(
    settings.redis_url, 
    socket_timeout=2.0, 
    socket_connect_timeout=2.0
)

__all__ = ["redis_client"]
