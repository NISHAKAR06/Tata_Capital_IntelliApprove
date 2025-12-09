import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project
    project_name: str = "Tata Capital IntelliApprove"
    environment: str = Field(default="local", env="ENVIRONMENT")
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])  # tighten in prod

    # LLM / Gemini
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model_flash: str = "gemini-1.5-flash-001"
    gemini_model_pro: str = "gemini-1.5-pro-001"
    gemini_model_vision: str = "gemini-1.5-pro-vision-001"

    # OpenAI (fallback / LLM enhancements)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-5.1-codex-max-preview", env="LLM_MODEL")

    # GCP Auth
    gcp_service_account_json: Optional[str] = Field(default=None, env="GCP_SERVICE_ACCOUNT_JSON")
    gcp_bucket_name: str = Field(default="tata-capital-docs", env="GCP_BUCKET_NAME")
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")

    # Third-party APIs
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone: Optional[str] = Field(default=None, env="TWILIO_PHONE")

    whatsapp_api_token: Optional[str] = Field(default=None, env="WHATSAPP_API_TOKEN")
    whatsapp_phone_id: Optional[str] = Field(default=None, env="WHATSAPP_PHONE_ID")

    # Bureau & CRM (mock for now)
    bureau_api_base: str = Field(default="http://mock-bureau.internal", env="BUREAU_API_BASE")
    bureau_api_key: Optional[str] = Field(default=None, env="BUREAU_API_KEY")

    crm_api_base: str = Field(default="http://mock-crm.internal", env="CRM_API_BASE")
    crm_api_key: Optional[str] = Field(default=None, env="CRM_API_KEY")

    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/tata_capital_loan",
        env="DATABASE_URL"
    )

    # Redis / Cache
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Security / PII
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    pii_masking_enabled: bool = Field(default=True, env="PII_MASKING_ENABLED")

    # Feature flags
    enable_voice: bool = Field(default=True, env="ENABLE_VOICE")
    enable_ocr: bool = Field(default=True, env="ENABLE_OCR")
    enable_gamification: bool = Field(default=True, env="ENABLE_GAMIFICATION")
    enable_explainability: bool = Field(default=True, env="ENABLE_EXPLAINABILITY")

    # Timeouts
    request_timeout_seconds: int = Field(default=30, env="REQUEST_TIMEOUT_SECONDS")
    long_task_timeout_seconds: int = Field(default=120, env="LONG_TASK_TIMEOUT_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
