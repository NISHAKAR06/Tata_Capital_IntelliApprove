"""Sales stage agent powered by Gemini Flash."""
from __future__ import annotations

from typing import Dict

from app.config.gemini_client import GeminiClient
from app.config.settings import get_settings


class SalesAgent:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = GeminiClient(model=settings.gemini_model_flash)

    def craft_pitch(self, context: Dict[str, str | float], user_message: str = "") -> str:
        if not self._client.available:
            return (
                "Hi! I can help you with personal loans. Share the amount and tenure "
                "you are looking for so that I can compute an indicative EMI."
            )
        
        prompt = (
            "You are 'IntelliApprove', a helpful and empathetic AI loan agent for Tata Capital. "
            "Your goal is to assist customers with personal loans, explain offers, and guide them. "
            "CONTEXT DATA:\n" + str(context) + "\n\n"
            "INSTRUCTIONS:\n"
            "1. Answer the user's message directly and naturally.\n"
            "2. If they ask about loans/offers, use the CONTEXT DATA (Amount, Tenure, EMI, Rate).\n"
            "3. If they ask who you are, introduce yourself as Tata Capital's AI assistant.\n"
            "4. Keep it concise (<80 words) and professional yet warm.\n"
            "5. Do not hallucinate offers not in the context."
        )
        
        response = self._client.generate(prompt, f"USER SAYS: {user_message}", max_tokens=200)
        return response or "I'm here to help with your loan application. Could you tell me more about what you need?"