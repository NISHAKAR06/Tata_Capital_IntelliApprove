"""Emotion detection from user text using Ollama."""
from typing import Dict, Optional

from app.config.ollama_client import OllamaClient
from app.config.settings import get_settings
from app.orchestrator.prompts import get_emotion_system_prompt

class EmotionDetector:
    """Detect emotional state from user input using LLM."""

    @staticmethod
    def detect(text: str) -> Dict[str, any]:
        """Detect emotion from text; return {primary, confidence}."""
        settings = get_settings()
        # Use per-agent Ollama model when configured, otherwise default
        model_name = settings.ollama_model_master or settings.ollama_model_default
        client = OllamaClient(model=model_name)
        
        if not client.available:
            # Fallback to rule-based if LLM is down
            return EmotionDetector._rule_based_detect(text)

        system_prompt = get_emotion_system_prompt() or (
            "You are an emotion classifier for Tata Capital's loan assistant. "
            "Classify each message into joy, neutral, anxiety, anger, sadness, or confusion and return JSON."
        )
        
        try:
            response = client.generate(system_prompt, text, max_tokens=50)
            import json
            # Clean up potential markdown code blocks
            cleaned = response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception:
            return EmotionDetector._rule_based_detect(text)

    @staticmethod
    def _rule_based_detect(text: str) -> Dict[str, any]:
        # Keyword mappings for emotions
        EMOTION_KEYWORDS = {
            "anxiety": ["worried", "anxious", "nervous", "unsure", "hesitant", "confused", "डर", "चिंता"],
            "joy": ["happy", "excited", "great", "awesome", "excellent", "खुश", "अच्छा"],
            "anger": ["angry", "frustrated", "upset", "annoyed", "गुस्सा", "परेशान"],
            "sadness": ["sad", "disappointed", "down", "upset", "उदास", "निराश"],
            "confusion": ["confused", "unclear", "explain", "understand", "मुझे समझ नहीं", "क्या है"],
            "neutral": [],
        }

        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}

        for emotion, keywords in EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    emotion_scores[emotion] += 1

        if not any(emotion_scores.values()):
            return {"primary": "neutral", "confidence": 1.0}

        primary = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[primary]
        total_matches = sum(emotion_scores.values())
        confidence = min(max_score / total_matches if total_matches > 0 else 0, 1.0)

        return {"primary": primary, "confidence": confidence}
