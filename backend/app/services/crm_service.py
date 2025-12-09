"""Lightweight CRM service stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.utils.id_masker import mask_identifier


@dataclass
class CRMContact:
    customer_id: str
    full_name: str
    phone: str
    loyalty_years: int
    auto_debit_enabled: bool
    utilization_lt_30: bool
    is_home_loan_customer: bool = False


class CRMService:
    def get_customer_profile(self, customer_id: Optional[str]) -> Dict[str, Any]:
        if not customer_id:
            return {}

        profile = CRMContact(
            customer_id=customer_id,
            full_name="Tata Capital Customer",
            phone="9876543210",
            loyalty_years=4,
            auto_debit_enabled=True,
            utilization_lt_30=True,
        )
        return {
            "customer_id": profile.customer_id,
            "full_name": profile.full_name,
            "masked_phone": mask_identifier(profile.phone),
            "loyalty_years": profile.loyalty_years,
            "auto_debit_enabled": profile.auto_debit_enabled,
            "utilization_lt_30": profile.utilization_lt_30,
            "is_home_loan_customer": profile.is_home_loan_customer,
        }
