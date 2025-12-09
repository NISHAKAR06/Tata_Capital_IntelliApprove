"""Retry helper for background tasks."""
from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 3, delay_seconds: float = 0.5) -> T:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return operation()
        except Exception as exc:  # pragma: no cover - best effort helper
            last_error = exc
            time.sleep(delay_seconds)
    if last_error:
        raise last_error
    raise RuntimeError("retry failed")
