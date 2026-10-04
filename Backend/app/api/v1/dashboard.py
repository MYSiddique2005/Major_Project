from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_service
from app.schemas.dashboard import DashboardSummary, SalesTrendPoint, StatusCount
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(require_permission(Permission.DASHBOARD_VIEW))]
)


@router.get("/summary", response_model=DashboardSummary, summary="Headline KPIs across all ERP modules")
def summary(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_summary()


@router.get("/sales-trend", response_model=list[SalesTrendPoint], summary="Monthly revenue for the last 12 months")
def sales_trend(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_sales_trend()


@router.get("/inventory-status", response_model=list[StatusCount], summary="Inventory records per stock status")
def inventory_status(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_inventory_status()


@router.get("/procurement-status", response_model=list[StatusCount], summary="Purchase orders per status")
def procurement_status(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_procurement_status()
