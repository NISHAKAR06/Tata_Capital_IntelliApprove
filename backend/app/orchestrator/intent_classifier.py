"""
Intent classification from user text.
Uses keyword matching and simple NLP; can be upgraded to an LLM-powered classifier.
"""
from typing import Optional


class IntentClassifier:
    """Classify user intent (e.g., ask_loan, verify, upload_docs, escalate)."""

    INTENTS = {
        "ask_loan": ["loan", "borrow", "amount", "credit", "interest", "emi"],
        "verify_kyc": ["verify", "otp", "identity", "confirm", "phone"],
        "upload_docs": ["upload", "document", "salary", "slip", "file"],
        "ask_rate": ["rate", "interest", "percentage", "% p.a.", "charges"],
        "ask_emi": ["emi", "monthly", "installment", "payment"],
        "ask_timeline": ["how long", "timeline", "days", "when", "approval"],
        "escalate": ["human", "speak", "agent", "representative", "मनुष्य"],
        "abandon": ["no thanks", "later", "goodbye", "exit", "quit"],
        "positive_interest": ["yes", "i want loan", "tell me more", "interested", "proceed", "apply", "ok"],
        "negative": ["not interested", "no thanks", "cancel"],
        "proceed_agreement": ["ok proceed", "let's do it", "apply now", "agree", "done"],
        "modification_request": ["lower emi", "different tenure", "change", "modify", "reduce"],
        "otp_submission": ["otp is", "code is", "1234", "5678", "here is otp"], # Simplified
        "kyc_mismatch": ["wrong details", "incorrect", "not me", "error"],
    }

    @staticmethod
    def classify(text: str) -> tuple[Optional[str], float]:
        """Classify intent; return (intent_name, confidence)."""

        text_lower = text.lower()
        intent_scores = {intent: 0 for intent in IntentClassifier.INTENTS}

        for intent, keywords in IntentClassifier.INTENTS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    intent_scores[intent] += 1

        if not any(intent_scores.values()):
            return (None, 0.0)

        primary = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[primary]
        total_matches = sum(intent_scores.values())
        confidence = min(max_score / total_matches if total_matches > 0 else 0, 1.0)

        return (primary, confidence)
