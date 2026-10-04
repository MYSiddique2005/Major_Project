from fastapi import APIRouter, Depends, Query

from app.api.deps import get_analytics_service
from app.models.enums import RiskLevel
from app.schemas.analytics import (
    DemandForecast,
    ForecastMethod,
    RiskAlert,
    StockRiskItem,
    SupplierPerformanceItem,
    WhatIfRequest,
    WhatIfResult,
)
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/analytics", tags=["Analytics"], dependencies=[Depends(require_permission(Permission.ANALYTICS_VIEW))]
)


@router.get(
    "/stock-risk",
    response_model=list[StockRiskItem],
    summary="Stockout risk per product (most urgent first)",
    description="Combines stock on hand, recent sales, supplier lead time and open purchase orders "
    "using fixed rules. Each item lists the facts behind its risk level.",
)
def list_stock_risk(
    level: RiskLevel | None = None,
    search: str | None = None,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.list_stock_risk(level, search)


@router.get("/stock-risk/{product_id}", response_model=StockRiskItem, summary="Stockout risk for one product")
def get_stock_risk(product_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_stock_risk(product_id)


@router.get(
    "/forecast/{product_id}",
    response_model=DemandForecast,
    summary="Weekly demand history and forecast for a product",
    description="Statistical forecast (moving average or linear trend). Without `method`, the one with the "
    "lower backtest error is used.",
)
def get_forecast(
    product_id: str,
    horizon_weeks: int = Query(default=8, ge=1, le=26),
    method: ForecastMethod | None = None,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_forecast(product_id, horizon_weeks, method)


@router.get(
    "/supplier-performance",
    response_model=list[SupplierPerformanceItem],
    summary="Delivery performance per supplier, from purchase-order history",
)
def list_supplier_performance(service: AnalyticsService = Depends(get_analytics_service)):
    return service.list_supplier_performance()


@router.get(
    "/alerts",
    response_model=list[RiskAlert],
    summary="High and critical stock and supplier risks",
    description="Produced by rule-based analytics, not by an AI model.",
)
def list_alerts(service: AnalyticsService = Depends(get_analytics_service)):
    return service.list_alerts()


@router.post(
    "/what-if",
    response_model=WhatIfResult,
    summary="Project stock under a changed demand, lead time or order quantity",
    description="Read-only simulation; nothing is saved and no order is created.",
)
def run_what_if(request: WhatIfRequest, service: AnalyticsService = Depends(get_analytics_service)):
    return service.run_what_if(request)
