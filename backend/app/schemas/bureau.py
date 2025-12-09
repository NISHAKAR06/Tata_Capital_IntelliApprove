from pydantic import BaseModel


class BureauReport(BaseModel):
    score: int
    bureau: str = "DemoBureau"
    utilization: float = 0.35
    accounts: int = 3
