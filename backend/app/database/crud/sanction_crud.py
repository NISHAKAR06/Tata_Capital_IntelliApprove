from app.database.db_connection import SessionLocal
from app.database.models.sanctions import Sanction  # type: ignore

def create_sanction(session, **kwargs):
    obj = Sanction(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
