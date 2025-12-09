"""Customer master table."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.db_connection import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    credit_score = Column(Integer, nullable=True)
    monthly_income = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
