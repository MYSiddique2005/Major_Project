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
    # Gemini only: models to move on to, in order, when the one in use is overloaded (503) or has used up
    # its daily free-tier requests. Each model has its own quota. Comma-separated; empty to disable.
    llm_fallback_model: str = "gemini-3.5-flash,gemini-3.5-flash-lite"
    llm_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"  # Anthropic only
    llm_max_tool_rounds: int = 8  # tool-calling round trips allowed for one question
    # Grounding: give the model the company's definitions and rules from the knowledge base.
    # Turn off only to measure what grounding contributes.
    llm_grounding: bool = True
    llm_knowledge_passages: int = 4  # passages retrieved for each question
    # Proactive scan: the assistant analyses the current high and critical findings on its own.
    insight_scan_interval_minutes: int = 1440  # 0 switches the scheduled scan off; it can still be run by hand
    insight_max_findings: int = 6  # findings analysed per scan, most severe first

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
