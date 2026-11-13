from fastapi import APIRouter, Depends

from app.api.deps import get_clock
from app.core.clock import Clock
from app.core.config import APP_VERSION, get_settings
from app.llm.providers import DEFAULT_MODELS
from app.schemas.system import SystemInfo
from app.security.authentication import get_current_user

router = APIRouter(prefix="/system", tags=["System"], dependencies=[Depends(get_current_user)])

CURRENT_PHASE = 9  # all nine phases are complete


@router.get("/info", response_model=SystemInfo, summary="Version, data backend and AI configuration in use")
def info(clock: Clock = Depends(get_clock)) -> SystemInfo:
    settings = get_settings()
    key = settings.gemini_api_key if settings.llm_provider == "gemini" else settings.anthropic_api_key
    return SystemInfo(
        app_name=settings.app_name,
        version=APP_VERSION,
        phase=CURRENT_PHASE,
        data_backend=settings.data_backend,
        persistent=settings.data_backend == "postgres",
        business_date=clock.today(),
        ai_configured=bool(key),
        ai_provider=settings.llm_provider,
        ai_model=settings.llm_model or DEFAULT_MODELS[settings.llm_provider],
        grounding=settings.llm_grounding,
        verifier=settings.llm_verifier,
    )
