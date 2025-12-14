from app.database.db_connection import SessionLocal
from app.database.models.gamification import Gamification  # type: ignore

def create_gamification(session, **kwargs):
    obj = Gamification(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
