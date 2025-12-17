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
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:8080", "http://localhost:5173", "*"])  # Allow frontend

    # LLM / Ollama
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER", description="LLM provider identifier (currently only 'ollama' is supported)")
    # Example env:
    #   OLLAMA_BASE_URL=http://localhost:11434
    #   OLLAMA_MODEL_DEFAULT=mistral
    #   OLLAMA_MODEL_UNDERWRITING=llama2
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    # Default Ollama model for most agents (fallback)
    ollama_model_default: Optional[str] = Field(default="llama3", env="OLLAMA_MODEL_DEFAULT")
    # Per-agent Ollama models so each agent can use a fine-tuned model
    ollama_model_master: Optional[str] = Field(default=None, env="OLLAMA_MODEL_MASTER")
    ollama_model_sales: Optional[str] = Field(default=None, env="OLLAMA_MODEL_SALES")
    ollama_model_verification: Optional[str] = Field(default=None, env="OLLAMA_MODEL_VERIFICATION")
    ollama_model_sanction: Optional[str] = Field(default=None, env="OLLAMA_MODEL_SANCTION")
    ollama_model_underwriting: Optional[str] = Field(default=None, env="OLLAMA_MODEL_UNDERWRITING")

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

    # Bureau, CRM, OfferMart, Notification (mock microservices in local dev)
    # Defaults point to the local FastAPI mock servers started via scripts.run_mock_servers
    bureau_api_base: str = Field(default="http://localhost:8002/api/credit-bureau", env="BUREAU_API_BASE")
    bureau_api_key: Optional[str] = Field(default=None, env="BUREAU_API_KEY")

    crm_api_base: str = Field(default="http://localhost:8001/api/crm", env="CRM_API_BASE")
    crm_api_key: Optional[str] = Field(default=None, env="CRM_API_KEY")

    offermart_api_base: str = Field(default="http://localhost:8003/api/offer-mart", env="OFFERMART_API_BASE")
    notification_api_base: str = Field(default="http://localhost:8004/api/notification", env="NOTIFICATION_API_BASE")

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

    # Vector search / embeddings (Weaviate + Sentence-Transformers)
    embeddings_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDINGS_MODEL_NAME",
    )
    weaviate_url: str = Field(default="http://localhost:8090", env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")

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
