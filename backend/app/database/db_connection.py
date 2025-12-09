"""SQLAlchemy session management."""
from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from app.config.settings import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
_engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=_engine, autoflush=False, autocommit=False))


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
