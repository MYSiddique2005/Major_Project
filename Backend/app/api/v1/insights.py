from fastapi import APIRouter, Depends, status

from app.api.deps import get_ai_action_service, get_insight_service
from app.models.entities import User
from app.models.enums import InsightStatus
from app.schemas.insights import InsightResponse, ScanResponse
from app.schemas.procurement import PurchaseOrderResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.ai_action_service import AIActionService
from app.services.insight_service import InsightService

router = APIRouter(
    prefix="/ai/insights", tags=["AI Insights"], dependencies=[Depends(require_permission(Permission.ANALYTICS_VIEW))]
)


@router.get(
    "",
    response_model=list[InsightResponse],
    summary="Insights the AI assistant raised on its own (most severe first)",
    description="New and acknowledged insights by default. Each carries the checks the server ran on it.",
)
def list_insights(
    status: InsightStatus | None = None,
    include_past: bool = False,
    service: InsightService = Depends(get_insight_service),
):
    return service.list_insights(status, include_past)


@router.get("/scans", response_model=list[ScanResponse], summary="Recent scans, newest first")
def list_scans(limit: int = 10, service: InsightService = Depends(get_insight_service)):
    return service.list_scans(limit)


@router.post(
    "/scan",
    response_model=ScanResponse,
    summary="Run a scan now",
    description="Analyses the current high and critical findings with one model request and stores an insight "
    "for each. Scans also run on a schedule (`INSIGHT_SCAN_INTERVAL_MINUTES`).",
)
def run_scan(
    user: User = Depends(require_permission(Permission.AI_USE)),
    service: InsightService = Depends(get_insight_service),
):
    return service.run_scan(trigger=user.username, user=user)


@router.post("/{insight_id}/acknowledge", response_model=InsightResponse, summary="Mark an insight as seen")
def acknowledge(
    insight_id: str,
    user: User = Depends(require_permission(Permission.AI_USE)),
    service: InsightService = Depends(get_insight_service),
):
    return service.review(insight_id, user, InsightStatus.ACKNOWLEDGED)


@router.post("/{insight_id}/dismiss", response_model=InsightResponse, summary="Dismiss an insight")
def dismiss(
    insight_id: str,
    user: User = Depends(require_permission(Permission.AI_USE)),
    service: InsightService = Depends(get_insight_service),
):
    return service.review(insight_id, user, InsightStatus.DISMISSED)


@router.post(
    "/{insight_id}/draft-order",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a draft purchase order from a reorder insight",
    description="Saves a Draft marked as coming from the insight, and marks the insight acknowledged. The draft "
    "then needs the usual submission and approval; nothing is ordered.",
)
def draft_order(
    insight_id: str,
    user: User = Depends(require_permission(Permission.PROCUREMENT_CREATE)),
    service: AIActionService = Depends(get_ai_action_service),
):
    return service.draft_from_insight(insight_id, user)
