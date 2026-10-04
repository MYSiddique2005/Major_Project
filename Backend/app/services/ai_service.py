"""Placeholder for the future LLM layer (Phase 4+).

No model is called anywhere yet. The method signature and response shape are
the contract the frontend already uses, so the internals can be replaced later
without touching the API or UI. The deterministic analytics the LLM will build
on live in app/services/analytics_service.py.
"""
from app.schemas.ai import ChatResponse


class AIService:
    def chat(self, message: str) -> ChatResponse:
        return ChatResponse(
            status="not_implemented",
            message="LLM functionality will be implemented in a future phase.",
        )
