from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_sales: float
    total_orders: int
    inventory_items: int
    low_stock_items: int
    critical_stock_items: int
    out_of_stock_items: int
    pending_purchase_orders: int
    active_suppliers: int


class SalesTrendPoint(BaseModel):
    month: str  # YYYY-MM
    label: str  # e.g. "Oct 2026"
    revenue: float
    orders: int


class StatusCount(BaseModel):
    status: str
    count: int
