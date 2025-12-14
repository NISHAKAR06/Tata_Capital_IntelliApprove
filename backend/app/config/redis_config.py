"""Redis configuration shim."""
from __future__ import annotations

import redis
from app.config.settings import get_settings

settings = get_settings()
redis_client = redis.Redis.from_url(settings.redis_url)

__all__ = ["redis_client"]
