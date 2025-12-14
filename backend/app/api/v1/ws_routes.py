"""WebSocket chat route wired to the orchestrator.

Supports two payload styles:
- Simple chat message: {"text", "language", "timestamp", ...}
- Full OrchestratorRequest JSON (advanced clients)
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.dependencies import get_logger, get_orchestrator
from app.schemas.conversation_state import OrchestratorRequest, OrchestratorResponse


router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/chat/{session_id}")
async def websocket_chat(
    ws: WebSocket,
    session_id: str,
    orchestrator = Depends(get_orchestrator),
):
    logger = get_logger()
    await ws.accept()

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data: Any = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "Invalid JSON payload"}))
                continue

            # Case 1: Simple payload from frontend as per design doc
            # Supports either {"text": "..."} or {"type": "init", "user_input": "..."}
            if isinstance(data, dict) and ("text" in data or "user_input" in data):
                user_message = data.get("text") or data.get("user_input") or ""
                language = data.get("language") or "en"

                resp_payload: dict[str, Any] = await orchestrator.process_message(
                    session_id=session_id,
                    user_input=user_message,
                    language=language,
                    context={
                        "channel": data.get("channel", "web"),
                        "timestamp": data.get("timestamp"),
                    },
                )
                await ws.send_text(json.dumps(resp_payload))

                if resp_payload.get("action") == "end":
                    break
                continue

            # Case 2: Full OrchestratorRequest payload
            try:
                req = OrchestratorRequest(**data)
            except Exception as exc:  # pydantic validation
                logger.warning("invalid orchestrator WS payload", extra={"error": str(exc)})
                await ws.send_text(json.dumps({"error": "Invalid request schema"}))
                continue

            if not req.state.conversation_id:
                req.state.conversation_id = session_id

            resp: OrchestratorResponse = await orchestrator.orchestrate(req)
            await ws.send_text(resp.json())

            if resp.next_action == "end":
                break

    except WebSocketDisconnect:
        logger.info("websocket disconnected", extra={"session_id": session_id})
    finally:
        await ws.close()
