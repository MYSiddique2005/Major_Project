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

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
