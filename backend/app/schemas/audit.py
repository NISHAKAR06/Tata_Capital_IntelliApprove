from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class AuditEntry(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    input_snapshot: Dict[str, Any]
    output_snapshot: Dict[str, Any]
    model_version: str | None = None
