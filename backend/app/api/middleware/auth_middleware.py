"""Auth middleware placeholder (JWT/token validation)."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # TODO: validate token
        return await call_next(request)
