"""Sanction letter persistence model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.db_connection import Base


class Sanction(Base):
    __tablename__ = "sanctions"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False)
    sanction_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    rate_percent = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    pdf_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
"""Sanction letters table."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.db_connection import Base


class Sanction(Base):
    __tablename__ = "sanctions"

    sanction_number = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    rate_percent = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    pdf_url = Column(String, nullable=False)
    valid_until = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
