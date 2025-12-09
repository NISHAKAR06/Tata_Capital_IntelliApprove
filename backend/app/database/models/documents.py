"""Uploaded document persistence model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String

from app.database.db_connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False)
    object_name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    kind = Column(String, nullable=False)  # e.g., 'salary_slip'
    net_salary = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
"""Uploaded documents metadata."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.database.db_connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
