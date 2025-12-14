"""Helper utilities for loading orchestrator system prompts.

Each agent (master, sales, verification, underwriting, sanction, emotion)
can load its base system prompt from the corresponding ``*_system_prompt.txt``
file in this package so prompts are editable without changing code.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

_BASE_DIR = Path(__file__).resolve().parent


def _load(name: str) -> str:
	path = _BASE_DIR / f"{name}_system_prompt.txt"
	try:
		return path.read_text(encoding="utf-8").strip()
	except FileNotFoundError:
		return ""


def get_master_system_prompt() -> str:
	return _load("master")


def get_sales_system_prompt() -> str:
	return _load("sales")


def get_emotion_system_prompt() -> str:
	return _load("emotion")


def get_verification_system_prompt() -> str:
	return _load("verification")


def get_underwriting_system_prompt() -> str:
	return _load("underwriting")


def get_sanction_system_prompt() -> str:
	return _load("sanction")

