import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.config.settings import get_settings

KEYS_DIR = Path(__file__).resolve().parent / "keys"


class ServiceAccountNotFound(RuntimeError):
    pass


def load_service_account(key_file: str = "service_account.json") -> Dict[str, Any]:
    path = KEYS_DIR / key_file
    if not path.exists():
        raise ServiceAccountNotFound(f"Missing service account file: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_api_key(key_file: str) -> Optional[str]:
    path = KEYS_DIR / key_file
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("api_key")


class GCPAuthManager:
    """Manages GCP authentication for Gemini and other services."""

    def __init__(self):
        self.settings = get_settings()
        self._service_account = None
        self._load_service_account()

    def _load_service_account(self):
        """Load GCP service account from JSON (local file or env var)."""
        try:
            # First try env var, then fall back to local file
            if self.settings.gcp_service_account_json:
                if self.settings.gcp_service_account_json.startswith("{"):
                    # JSON string in env var
                    self._service_account = json.loads(self.settings.gcp_service_account_json)
                else:
                    # File path
                    with open(self.settings.gcp_service_account_json, "r") as f:
                        self._service_account = json.load(f)
            else:
                # Fall back to local file
                self._service_account = load_service_account()
        except Exception as e:
            print(f"⚠️  Warning: Could not load GCP service account: {e}")

    @property
    def is_authenticated(self) -> bool:
        return self._service_account is not None and bool(self.settings.gemini_api_key)

    @property
    def service_account(self) -> Optional[dict]:
        return self._service_account

    @property
    def project_id(self) -> Optional[str]:
        return self.settings.gcp_project_id or (self._service_account.get("project_id") if self._service_account else None)


gcp_auth = GCPAuthManager()
