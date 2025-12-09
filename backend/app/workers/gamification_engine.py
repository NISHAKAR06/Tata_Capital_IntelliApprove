"""Gamification nudges for the chat experience."""
from __future__ import annotations

from typing import Dict


class GamificationEngine:
    def assign_badge(self, stage: str, intents_completed: int) -> Dict[str, str]:
        if stage == "SANCTION":
            badge = "Deal Closer"
        elif intents_completed > 3:
            badge = "Loan Pro"
        else:
            badge = "Getting Started"
        return {"badge": badge, "message": f"Unlocked badge: {badge}"}
