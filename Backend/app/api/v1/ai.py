from typing import Literal

from fastapi import APIRouter, Depends

from app.api.deps import get_ai_service
from app.models.entities import User
from app.knowledge.base import CATEGORIES
from app.knowledge.content import get_knowledge_base
from app.schemas.ai import ChatRequest, ChatResponse, KnowledgeEntry
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the AI assistant a question about the ERP data",
    description="The assistant answers by calling read-only ERP tools with the caller's permissions; `sources` "
    "lists the calls it made. Returns `status: not_configured` when no API key is set.",
)
def chat(
    request: ChatRequest,
    user: User = Depends(require_permission(Permission.AI_USE)),
    service: AIService = Depends(get_ai_service),
):
    return service.chat(request.message, user, request.history)


@router.get(
    "/knowledge",
    response_model=list[KnowledgeEntry],
    summary="Browse or search the knowledge base the assistant is grounded in",
    description="Without `search`, every passage is returned. With it, the most relevant passages are returned "
    "best first, ranked the same way as for the assistant.",
    dependencies=[Depends(require_permission(Permission.AI_USE))],
)
def knowledge(search: str | None = None, category: Literal[CATEGORIES] | None = None, limit: int = 10):
    base = get_knowledge_base()
    if search:
        return [
            KnowledgeEntry(**match.entry.summary(), text=match.entry.text, score=match.score)
            for match in base.search(search, limit, category)
        ]
    return [
        KnowledgeEntry(**entry.summary(), text=entry.text)
        for entry in base.entries
        if category is None or entry.category == category
    ]
