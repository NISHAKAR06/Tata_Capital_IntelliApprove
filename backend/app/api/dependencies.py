"""FastAPI dependency wiring helpers."""
from __future__ import annotations

import logging
from functools import lru_cache

from app.config.settings import Settings, get_settings
from app.orchestrator.master_orchestrator import MasterOrchestrator
from app.services.audio_service import AudioService
from app.services.otp_service import OTPService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService

_logger = logging.getLogger("intelliapprove")


@lru_cache
def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_orchestrator() -> MasterOrchestrator:
    return MasterOrchestrator()


def get_logger() -> logging.Logger:
    return _logger


def get_storage_service() -> StorageService:
    return StorageService()


def get_pdf_service() -> PDFService:
    return PDFService()


def get_otp_service() -> OTPService:
    return OTPService()


def get_audio_service() -> AudioService:
    return AudioService()
