"""Background scheduler for nudges."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List


class FollowUpScheduler:
    def plan_reminders(self, conversation_id: str) -> List[Dict[str, str]]:
        now = datetime.now(tz=timezone.utc)
        reminders = [
            {"conversation_id": conversation_id, "send_at": (now + timedelta(hours=4)).isoformat()},
            {"conversation_id": conversation_id, "send_at": (now + timedelta(days=1)).isoformat()},
        ]
        return reminders
