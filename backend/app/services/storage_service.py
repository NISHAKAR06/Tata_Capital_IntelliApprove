"""Local storage wrapper used for uploads."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from app.config.settings import get_settings


class StorageService:
    def __init__(self, base_path: Optional[Path] = None) -> None:
        settings = get_settings()
        upload_dir = base_path or Path("storage/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        self._upload_dir = upload_dir
        self._bucket_name = settings.gcp_bucket_name

    def upload_bytes(self, *, conversation_id: str, filename: str, data: bytes) -> str:
        suffix = Path(filename).suffix
        object_name = f"{conversation_id}-{uuid.uuid4().hex}{suffix}"
        file_path = self._upload_dir / object_name
        file_path.write_bytes(data)
        return object_name

    def url_for(self, object_name: str) -> str:
        return f"gs://{self._bucket_name}/{object_name}"
