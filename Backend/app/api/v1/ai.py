from fastapi import APIRouter, Depends

from app.api.deps import get_ai_service
from app.schemas.ai import ChatRequest, ChatResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Placeholder"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI assistant (placeholder - no LLM is called)",
    description="Currently always returns `status: not_implemented`. The request/response shape is the "
    "contract the future LLM layer will fulfil.",
    dependencies=[Depends(require_permission(Permission.AI_USE))],
)
def chat(request: ChatRequest, service: AIService = Depends(get_ai_service)):
    return service.chat(request.message)
