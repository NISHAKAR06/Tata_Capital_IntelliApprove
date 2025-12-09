from typing import Optional

from pydantic import BaseModel


class OCRResult(BaseModel):
    status: str
    file_id: Optional[str] = None
    gross_salary: Optional[float] = None
    net_salary: Optional[float] = None
    employer: Optional[str] = None
    month: Optional[str] = None
    confidence: Optional[float] = None
