from __future__ import annotations

from typing import Optional
from app.config.redis_config import redis_client

PREFIX = "otp:"

def set_otp(phone: str, code: str, ttl: int = 300) -> None:
    redis_client.set(PREFIX + phone, code, ex=ttl)

def get_otp(phone: str) -> Optional[str]:
    v = redis_client.get(PREFIX + phone)
    return v.decode() if v else None
