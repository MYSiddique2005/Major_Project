from fastapi import APIRouter, Depends

from app.api.deps import get_clock
from app.core.clock import Clock
from app.core.config import get_settings
from app.schemas.system import SystemInfo
from app.security.authentication import get_current_user

router = APIRouter(prefix="/system", tags=["System"], dependencies=[Depends(get_current_user)])

CURRENT_PHASE = 8


@router.get("/info", response_model=SystemInfo, summary="Build phase and data backend in use")
def info(clock: Clock = Depends(get_clock)) -> SystemInfo:
    settings = get_settings()
    return SystemInfo(
        app_name=settings.app_name,
        phase=CURRENT_PHASE,
        data_backend=settings.data_backend,
        persistent=settings.data_backend == "postgres",
        business_date=clock.today(),
    )
