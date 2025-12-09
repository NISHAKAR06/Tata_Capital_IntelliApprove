"""Mask identifiers such as phone numbers or PAN."""
from __future__ import annotations


def mask_identifier(identifier: str, visible: int = 4) -> str:
    identifier = identifier or ""
    if len(identifier) <= visible:
        return "*" * len(identifier)
    hidden = max(len(identifier) - visible, 0)
    return f"{'*' * hidden}{identifier[-visible:]}"
