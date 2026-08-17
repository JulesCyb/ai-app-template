"""Zentrale Konfiguration. Werte kommen aus der Umgebung bzw. .env (siehe .env.example).

Mandantenspezifisches (Modellwahl, Prompts, Limits) gehört NICHT hierher, sondern in
tenants.settings – hier stehen nur prozessweite Einstellungen.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-app"
    environment: str = "dev"
    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    database_url_migrations: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"

    llm_model: str = "anthropic:claude-sonnet-4-5"
    litellm_base_url: str | None = None
    litellm_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    auth_mode: str = Field(default="dev-headers", pattern="^(dev-headers|jwt)$")

    langfuse_host: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None

    mcp_tenant_id: str | None = None
    mcp_user_id: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
