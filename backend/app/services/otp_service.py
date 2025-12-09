"""OTP delivery helper."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict

from app.utils.time_utils import utc_now_iso
from app.utils.validators import validate_otp, validate_phone_number


@dataclass
class OTPRecord:
    phone_number: str
    otp: str
    created_at: str
    verified: bool = False


class OTPService:
    _records: Dict[str, OTPRecord] = {}

    def send_otp(self, phone_number: str) -> OTPRecord:
        if not validate_phone_number(phone_number):
            raise ValueError("Invalid phone number")
        otp = f"{random.randint(100000, 999999)}"
        record = OTPRecord(phone_number=phone_number, otp=otp, created_at=utc_now_iso())
        self._records[phone_number] = record
        return record

    def verify_otp(self, phone_number: str, otp: str) -> bool:
        if not validate_otp(otp):
            return False
        record = self._records.get(phone_number)
        if record and record.otp == otp:
            record.verified = True
            return True
        return False
