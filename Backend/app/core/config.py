"""Application settings, loaded from environment variables / .env."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "IntelliERP"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-this-development-secret-before-deploying"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    frontend_url: str = "http://localhost:5173"

    # "postgres" persists data; "memory" serves the seed data from RAM and resets on restart.
    data_backend: Literal["postgres", "memory"] = "postgres"
    database_url: str = "postgresql+psycopg://intellierp:intellierp@localhost:5432/intellierp"

    # AI assistant. Without the provider's key the assistant reports that it is not configured.
    llm_provider: Literal["gemini", "anthropic"] = "gemini"
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_model: str | None = None  # default: gemini-3.8-flash or claude-opus-5-5, by provider
    # Gemini only: used when the main model stays unavailable (Google returns 503 when one is overloaded).
    llm_fallback_model: str | None = "gemini-3.5-flash"
    llm_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"  # Anthropic only
    llm_max_tool_rounds: int = 8  # tool-calling round trips allowed for one question
    # Grounding: give the model the company's definitions and rules from the knowledge base.
    # Turn off only to measure what grounding contributes.
    llm_grounding: bool = True
    llm_knowledge_passages: int = 4  # passages retrieved for each question

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
