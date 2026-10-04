from datetime import date

from pydantic import BaseModel, Field

from app.models.enums import PurchaseOrderStatus


class PurchaseOrderResponse(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    order_date: date
    expected_delivery: date
    actual_delivery: date | None
    status: PurchaseOrderStatus
    reason: str
    created_by: str


class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    product_id: str
    quantity: int = Field(gt=0, le=100_000)
    unit_price: float | None = Field(default=None, gt=0, description="Defaults to the product's standard unit cost")
    expected_delivery: date | None = Field(
        default=None, description="Defaults to today plus the supplier's average delivery time"
    )
    reason: str = Field(default="", max_length=500)


class PurchaseOrderUpdate(BaseModel):
    """Partial update; only drafts can be edited."""

    supplier_id: str | None = None
    product_id: str | None = None
    quantity: int | None = Field(default=None, gt=0, le=100_000)
    unit_price: float | None = Field(default=None, gt=0)
    expected_delivery: date | None = None
    reason: str | None = Field(default=None, max_length=500)
