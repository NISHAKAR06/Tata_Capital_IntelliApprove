"""Basic validation helpers used across services."""
from __future__ import annotations

import re

_PHONE_PATTERN = re.compile(r"^[6-9][0-9]{9}$")


def validate_phone_number(phone: str) -> bool:
    return bool(_PHONE_PATTERN.fullmatch(phone or ""))


def validate_otp(otp: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{4,6}", otp or ""))
