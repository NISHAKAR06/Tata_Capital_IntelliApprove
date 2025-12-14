"""CRM service that talks to the local CRM mock server."""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.config.settings import get_settings
from app.utils.id_masker import mask_identifier


class CRMService:
    """Fetch customer profile from the CRM mock service.

    The mock CRM is exposed by backend/mock_servers/crm_server.py and started
    on http://localhost:8001 by scripts.run_mock_servers.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.crm_api_base.rstrip("/")
        self.api_key = settings.crm_api_key
        self._timeout = settings.request_timeout_seconds

    def get_customer_profile(self, customer_id: Optional[str]) -> Dict[str, Any]:
        """Hydrate a customer profile given an identifier (PAN/customer_id).

        For the mock server, we treat the incoming customer_id as PAN number
        and call POST /api/crm/get-customer.
        """

        if not customer_id:
            return {}

        url = f"{self.base_url}/get-customer"
        payload = {"pan_number": str(customer_id)}

        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            body = resp.json()
        except Exception:
            # Fallback to a minimal synthetic profile if CRM is unavailable
            return {
                "customer_id": customer_id,
                "name": "Tata Capital Customer",
                "masked_phone": mask_identifier("9876543210"),
                "monthly_income": 80000,
            }

        if body.get("status") != "success" or not body.get("data"):
            return {
                "customer_id": customer_id,
                "name": "Unknown Customer",
            }

        data = body["data"]

        # Map CRM mock fields into our conversational profile schema
        phone = data.get("phone", "")
        profile: Dict[str, Any] = {
            "customer_id": str(data.get("pan_number") or customer_id),
            "name": data.get("name", "Tata Capital Customer"),
            "email": data.get("email"),
            "masked_phone": mask_identifier(phone) if phone else None,
            "phone": phone,
            "pan": data.get("pan_number"),
            "monthly_income": data.get("monthly_income"),
            "employment_type": data.get("employment_type"),
            "employer": data.get("company_name"),
            "years_employed": data.get("years_employed"),
            "address": data.get("address"),
            "bank_account": data.get("bank_account"),
            "bank_ifsc": data.get("bank_ifsc"),
        }

        # Convenience / backward-compat fields used by some agents
        if "pre_approved_limit" not in profile:
            # Rough demo heuristic: 4x monthly income
            income = data.get("monthly_income") or 80000
            profile["pre_approved_limit"] = int(income) * 4

        return profile
