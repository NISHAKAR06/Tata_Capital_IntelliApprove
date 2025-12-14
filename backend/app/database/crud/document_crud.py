from app.database.db_connection import SessionLocal
from app.database.models.documents import Document  # type: ignore

def create_document(session, **kwargs):
    obj = Document(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
