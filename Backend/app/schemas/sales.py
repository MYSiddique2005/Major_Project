from datetime import date

from pydantic import BaseModel

from app.models.enums import SalesStatus


class SalesOrderResponse(BaseModel):
    id: str
    customer: str
    product_id: str
    product_name: str
    sku: str
    quantity: int
    unit_price: float
    total_amount: float
    order_date: date
    status: SalesStatus


class SalesStats(BaseModel):
    total_revenue: float  # excludes cancelled orders
    total_orders: int
    average_order_value: float
    pending: int
    processing: int
    completed: int
    cancelled: int
