from typing import List, Optional

from pydantic import BaseModel


class ExplainabilityFactor(BaseModel):
    name: str
    value: Optional[str]
    threshold: Optional[str]
    status: str
    reason: Optional[str]
    points: Optional[int] = None


class UnderwritingExplainability(BaseModel):
    decision: Optional[str]
    summary: Optional[str]
    factors: List[ExplainabilityFactor]
    total_points: Optional[int] = None
    max_points: Optional[int] = None
