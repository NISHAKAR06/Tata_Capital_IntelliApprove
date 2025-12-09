"""Analytics tracker stub."""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("analytics")


class AnalyticsTracker:
    def track_event(self, name: str, payload: Dict[str, Any]) -> None:
        logger.debug("analytics event", extra={"event": name, **payload})
