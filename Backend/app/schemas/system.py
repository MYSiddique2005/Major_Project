from typing import Literal

from pydantic import BaseModel


class SystemInfo(BaseModel):
    app_name: str
    phase: int
    data_backend: Literal["postgres", "memory"]
    persistent: bool
