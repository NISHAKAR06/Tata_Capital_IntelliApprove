from app.database.db_connection import SessionLocal
from app.database.models.loan_applications import LoanApplication  # type: ignore

def create_application(session, **kwargs):
    obj = LoanApplication(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
