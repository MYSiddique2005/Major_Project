from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.schemas.system import SystemInfo
from app.security.authentication import get_current_user

router = APIRouter(prefix="/system", tags=["System"], dependencies=[Depends(get_current_user)])

CURRENT_PHASE = 6


@router.get("/info", response_model=SystemInfo, summary="Build phase and data backend in use")
def info() -> SystemInfo:
    settings = get_settings()
    return SystemInfo(
        app_name=settings.app_name,
        phase=CURRENT_PHASE,
        data_backend=settings.data_backend,
        persistent=settings.data_backend == "postgres",
    )
