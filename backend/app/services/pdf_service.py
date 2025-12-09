"""Generate sanction letters as PDFs (mock)."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict

from app.utils.time_utils import utc_now_iso


class PDFService:
    _output_dir = Path("storage/sanctions")

    def __init__(self) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_sanction_letter(self, payload: Dict[str, str | float]) -> Dict[str, str | float]:
        sanction_number = payload.get("sanction_number") or f"SAN-{uuid.uuid4().hex[:8].upper()}"
        file_name = f"{sanction_number}.pdf"
        file_path = self._output_dir / file_name
        file_path.write_text("Sanction letter placeholder", encoding="utf-8")
        return {
            **payload,
            "sanction_number": sanction_number,
            "pdf_url": f"/static/sanctions/{file_name}",
            "generated_at": utc_now_iso(),
        }
