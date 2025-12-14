"""Rate limiter placeholder."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # TODO: enforce rate limits via Redis
        return await call_next(request)
