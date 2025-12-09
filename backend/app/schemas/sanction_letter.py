from pydantic import BaseModel


class SanctionLetter(BaseModel):
    sanction_number: str
    amount: float
    tenure_months: int
    rate_percent: float
    emi: float
    pdf_url: str
    valid_until: str
