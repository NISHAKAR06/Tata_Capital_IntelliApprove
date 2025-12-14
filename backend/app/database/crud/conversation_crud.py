from app.database.db_connection import SessionLocal
from app.database.models.conversations import Conversation  # type: ignore

def get_conversation(session, conversation_id: str):
    return session.query(Conversation).filter_by(conversation_id=conversation_id).first()
