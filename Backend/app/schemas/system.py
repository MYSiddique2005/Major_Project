from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SystemInfo(BaseModel):
    app_name: str
    version: str
    phase: int = Field(description="The last completed build phase (9 of 9: the project is complete)")
    data_backend: Literal["postgres", "memory"]
    persistent: bool
    business_date: date  # the day the analytics treat as today (see app/core/clock.py)
    ai_configured: bool = Field(description="Whether the AI provider's API key is set")
    ai_provider: Literal["gemini", "anthropic"]
    ai_model: str
    grounding: bool = Field(description="Whether answers are grounded in the knowledge base")
    verifier: Literal["patterns", "trace-rule", "trace", "off"]
