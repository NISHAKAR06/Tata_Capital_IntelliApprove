"""Notification service backed by the local notification mock server.

Uses backend/mock_servers/email_sms_server.py running on port 8004 to
simulate email/SMS/WhatsApp notifications for sanction and disbursement.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.config.settings import get_settings


class NotificationService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.notification_api_base.rstrip("/")
        self._timeout = settings.request_timeout_seconds

    def _post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def send_sanction_notification(self, *, email: Optional[str], phone: Optional[str], customer_name: str, amount: float, tenure_months: int, rate: float, sanction_number: str) -> None:
        """Fire-and-forget sanction notification via multi-channel API.

        For the mock, we just call POST /send with a generic template.
        """

        if not email and not phone:
            return

        variables = {
            "name": customer_name,
            "amount": f"{amount:,.0f}",
            "tenure": tenure_months,
            "rate": f"{rate:.2f}",
            "sanction_number": sanction_number,
        }

        payload: Dict[str, Any] = {
            "customer_id": sanction_number,
            "customer_name": customer_name,
            "notification_type": "EMAIL" if email else "SMS",
            "template": "SANCTION_LETTER_READY",
            "variables": variables,
        }

        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone

        self._post("/send", payload)

    def send_disbursement_confirmation(self, *, email: Optional[str], phone: Optional[str], customer_name: str, net_amount: float, txn_id: str) -> None:
        if not email and not phone:
            return

        variables = {
            "name": customer_name,
            "amount": f"{net_amount:,.0f}",
            "transaction_id": txn_id,
        }

        payload: Dict[str, Any] = {
            "customer_id": txn_id,
            "customer_name": customer_name,
            "notification_type": "EMAIL" if email else "SMS",
            "template": "DISBURSEMENT_CONFIRMED",
            "variables": variables,
        }

        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone

        self._post("/send", payload)
