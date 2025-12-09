"""Conversation persistence model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String

from app.database.db_connection import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=True)
    state = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
