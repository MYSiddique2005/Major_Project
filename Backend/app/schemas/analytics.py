"""Contracts for the analytics endpoints. Everything here is produced by
deterministic rules and statistics (app/analytics); nothing is AI generated."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import RiskLevel, SupplierStatus

ForecastMethod = Literal["moving_average", "linear_trend"]


class StockRiskItem(BaseModel):
    product_id: str
    product_name: str
    sku: str
    category: str
    on_hand: int  # all warehouses
    safety_stock: int
    reorder_level: int
    avg_daily_demand: float
    previous_avg_daily_demand: float
    demand_trend_pct: float | None
    days_of_cover: float | None
    projected_stockout_date: date | None
    supplier_id: str
    supplier_name: str
    lead_time_days: float
    lead_time_source: Literal["observed deliveries", "supplier master data"]
    inbound_units: int
    next_inbound_date: date | None
    overdue_inbound_units: int
    awaiting_approval_units: int
    risk_level: RiskLevel
    drivers: list[str] = Field(description="Factual statements that explain the risk level")
    reorder_point: int
    suggested_order_quantity: int = Field(description="0 when no order is suggested")
    suggested_supplier_id: str | None
    suggested_supplier_name: str | None


class WeeklyDemand(BaseModel):
    week_start: date
    units: float


class DemandForecast(BaseModel):
    product_id: str
    product_name: str
    method: ForecastMethod
    method_selection: Literal["requested", "lowest backtest error"]
    history: list[WeeklyDemand]
    forecast: list[WeeklyDemand]
    avg_weekly_forecast: float
    backtest_wape: dict[ForecastMethod, float | None] = Field(
        description="One-week-ahead weighted absolute percentage error over the last 8 weeks, per method (0.2 = 20%)"
    )


class SupplierPerformanceItem(BaseModel):
    supplier_id: str
    supplier_name: str
    status: SupplierStatus
    orders_total: int
    deliveries_analyzed: int
    on_time_rate: float | None
    avg_delay_days: float | None
    max_delay_days: int | None
    avg_lead_time_days: float | None
    delay_trend: Literal["worsening", "improving", "stable", "insufficient data"]
    open_orders: int
    overdue_orders: int
    risk_level: RiskLevel
    drivers: list[str]


class RiskAlert(BaseModel):
    id: str
    category: Literal["Stockout Risk", "Supplier Risk"]
    severity: RiskLevel
    title: str
    message: str
    entity: Literal["product", "supplier"]
    entity_id: str
    source: str = "Rule-based analytics"


class WhatIfRequest(BaseModel):
    product_id: str
    demand_change_pct: float = Field(default=0, ge=-100, le=500, description="e.g. 30 = demand 30% higher")
    lead_time_change_days: int = Field(default=0, ge=-30, le=90, description="e.g. 5 = deliveries 5 days later")
    order_quantity: int = Field(default=0, ge=0, le=100_000, description="Units ordered today in the scenario")
    horizon_days: int = Field(default=60, ge=14, le=180)


class StockPoint(BaseModel):
    date: date
    stock: float


class WhatIfOutcome(BaseModel):
    daily_demand: float
    lead_time_days: float
    stockout_date: date | None
    days_until_stockout: int | None
    days_below_safety: int
    unmet_demand_units: float
    ending_stock: float
    points: list[StockPoint]


class WhatIfResult(BaseModel):
    product_id: str
    product_name: str
    on_hand: int
    safety_stock: int
    horizon_days: int
    baseline: WhatIfOutcome
    scenario: WhatIfOutcome
    assumptions: list[str]
