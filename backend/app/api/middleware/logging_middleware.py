"""Request/response logging middleware placeholder.

Currently unused; basic logging relies on FastAPI/Uvicorn defaults.
"""

from __future__ import annotations

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("request-logger")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info("%s %s -> %s in %.1fms", request.method, request.url.path, response.status_code, duration)
        return response
