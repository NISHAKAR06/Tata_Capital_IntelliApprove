from app.database.db_connection import SessionLocal
from app.database.models.customers import Customer  # type: ignore

def get_customer(session, customer_id: str):
    return session.query(Customer).filter_by(customer_id=customer_id).first()
