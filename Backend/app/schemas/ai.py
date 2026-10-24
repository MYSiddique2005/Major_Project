"""Contracts for the AI assistant."""
from typing import Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=20000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, examples=["Which products are at risk of stockout?"])
    history: list[ChatTurn] = Field(
        default=[], max_length=40, description="Earlier turns of this conversation, oldest first"
    )


class ChatResponse(BaseModel):
    status: str = Field(description="ok, not_configured, refused or incomplete")
    message: str
    sources: list[dict] = Field(default=[], description="The tool calls the answer is based on")
    knowledge: list[dict] = Field(default=[], description="Knowledge-base passages given to the model")
    recommendations: list[dict] = []
    actions: list[dict] = []
    unverified_figures: list[str] = Field(
        default=[], description="Figures in the answer found in no tool result, knowledge passage or question"
    )
    contradicted_claims: list[str] = Field(
        default=[], description="Statements in the answer that the system's data contradicts, after one correction"
    )
    verification: dict | None = Field(
        default=None, description="How the answer's statements were checked: verifier, statements checked, extraction"
    )
    provider: str | None = None
    model: str | None = None
    usage: dict[str, int] | None = None


class KnowledgeEntry(BaseModel):
    id: str
    title: str
    category: str
    text: str
    score: float | None = Field(default=None, description="Relevance to the search, when one was given")
