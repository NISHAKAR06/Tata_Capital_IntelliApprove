from __future__ import annotations

from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self._connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[session_id] = ws

    async def disconnect(self, session_id: str) -> None:
        ws = self._connections.pop(session_id, None)
        if ws:
            await ws.close()

    async def send_text(self, session_id: str, message: str) -> None:
        ws = self._connections.get(session_id)
        if ws:
            await ws.send_text(message)
