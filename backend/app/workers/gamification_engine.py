"""Gamification nudges for the chat experience."""
from __future__ import annotations

from typing import Dict


class GamificationEngine:
    def assign_badge(self, stage: str, intents_completed: int) -> Dict[str, str | int]:
        """Calculate points, level, and badges based on progress."""
        points = intents_completed * 10
        if stage == "SANCTION":
            points += 500
            badge = "Deal Closer"
            level = "Expert"
        elif stage == "UNDERWRITING":
            points += 200
            badge = "Financial Wizard"
            level = "Intermediate"
        elif intents_completed > 5:
            badge = "Loan Pro"
            level = "Advanced"
        else:
            badge = "Getting Started"
            level = "Novice"

        return {
            "badge": badge,
            "points": points,
            "level": level,
            "message": f"🎉 Level Up! You are now a {level}. Badge unlocked: {badge} (+{points} pts)"
        }
