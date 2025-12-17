"""Credit Bureau check endpoints.

These routes expose /api/credit-bureau/check-credit style APIs on the
main backend by proxying to the local credit bureau mock server.
"""
from __future__ import annotations

from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_app_settings
from app.config.settings import Settings

router = APIRouter(prefix="/credit-bureau", tags=["CreditBureau"])


class CreditCheckRequest(BaseModel):
    pan_number: str


@router.post("/check-credit")
async def check_credit(
    payload: CreditCheckRequest,
    settings: Settings = Depends(get_app_settings),
) -> Dict[str, Any]:
    """Call the mock credit bureau /check-credit endpoint and return its body."""

    base = settings.bureau_api_base.rstrip("/")
    url = f"{base}/check-credit"

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            resp = await client.post(url, json=payload.model_dump())
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network
        raise HTTPException(status_code=exc.response.status_code, detail="Credit bureau error") from exc
    except Exception as exc:  # pragma: no cover - network
        raise HTTPException(status_code=502, detail="Credit bureau service unavailable") from exc
