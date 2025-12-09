"""Admin utilities and health endpoints."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version")
def version() -> dict:
    return {"service": "intelliapprove-backend", "version": "0.1.0"}
