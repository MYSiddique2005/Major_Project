"""Contracts for the future AI layer. Only placeholders are returned so far."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, examples=["Which products are at risk of stockout?"])


class ChatResponse(BaseModel):
    status: str
    message: str
    sources: list[dict] = []
    recommendations: list[dict] = []
    actions: list[dict] = []
