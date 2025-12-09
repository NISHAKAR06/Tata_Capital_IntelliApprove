"""
Emotion detection from user text and ASR transcripts.
Uses rule-based and simple keyword matching for now; can be upgraded to Gemini.
"""
from typing import Dict, Optional


class EmotionDetector:
    """Detect emotional state from user input."""

    # Keyword mappings for emotions
    EMOTION_KEYWORDS = {
        "anxiety": ["worried", "anxious", "nervous", "unsure", "hesitant", "confused", "डर", "चिंता"],
        "joy": ["happy", "excited", "great", "awesome", "excellent", "खुश", "अच्छा"],
        "anger": ["angry", "frustrated", "upset", "annoyed", "गुस्सा", "परेशान"],
        "sadness": ["sad", "disappointed", "down", "upset", "उदास", "निराश"],
        "confusion": ["confused", "unclear", "explain", "understand", "मुझे समझ नहीं", "क्या है"],
        "neutral": [],
    }

    @staticmethod
    def detect(text: str) -> Dict[str, any]:
        """Detect emotion from text; return {primary, confidence}."""

        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in EmotionDetector.EMOTION_KEYWORDS}

        for emotion, keywords in EmotionDetector.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    emotion_scores[emotion] += 1

        if not any(emotion_scores.values()):
            return {"primary": "neutral", "confidence": 1.0}

        primary = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[primary]
        # Confidence = max_score / total_keyword_matches
        total_matches = sum(emotion_scores.values())
        confidence = min(max_score / total_matches if total_matches > 0 else 0, 1.0)

        return {"primary": primary, "confidence": confidence}
