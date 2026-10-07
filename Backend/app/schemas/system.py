from datetime import date
from typing import Literal

from pydantic import BaseModel


class SystemInfo(BaseModel):
    app_name: str
    phase: int
    data_backend: Literal["postgres", "memory"]
    persistent: bool
    business_date: date  # the day the analytics treat as today (see app/core/clock.py)
