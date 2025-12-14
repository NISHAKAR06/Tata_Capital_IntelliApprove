"""Global error handling middleware placeholder."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:  # noqa: BLE001
            return JSONResponse({"detail": str(e)}, status_code=500)
