"""WhatsApp notification publisher."""
from __future__ import annotations

from typing import Dict


class WhatsappSender:
    def send_template(self, phone_number: str, template: str, data: Dict[str, str]) -> Dict[str, str]:
        return {"status": "queued", "phone_number": phone_number, "template": template, "data": data}
