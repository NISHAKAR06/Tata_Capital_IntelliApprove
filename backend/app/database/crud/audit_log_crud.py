from app.database.db_connection import SessionLocal
from app.database.models.audit_logs import AuditLog  # type: ignore

def create_audit_log(session, **kwargs):
    obj = AuditLog(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
