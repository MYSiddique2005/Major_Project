"""Domain entities.

These are the records the repositories store and return. They mirror what the
relational tables will look like in Phase 2, so the SQLAlchemy models can map
onto them one-to-one. Derived values (stock status, totals, joined names) are
deliberately NOT stored here; services compute them.
"""
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import (
    ApprovalStatus,
    AuditStatus,
    ProductStatus,
    PurchaseOrderStatus,
    Role,
    SalesStatus,
    SupplierStatus,
)


class User(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    role: Role
    hashed_password: str
    is_active: bool = True


class Supplier(BaseModel):
    id: str
    name: str
    contact_name: str
    email: str
    phone: str
    country: str
    product_ids: list[str]
    avg_delivery_days: float
    delivery_reliability: float  # percentage of orders delivered on time, 0-100
    status: SupplierStatus


class Product(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    supplier_id: str  # primary supplier
    price: float  # selling price
    unit_cost: float  # standard purchase cost
    status: ProductStatus


class InventoryRecord(BaseModel):
    id: str
    product_id: str
    warehouse: str
    current_stock: int
    safety_stock: int
    reorder_level: int
    last_updated: date


class SalesOrder(BaseModel):
    id: str
    customer: str
    product_id: str
    quantity: int
    unit_price: float
    order_date: date
    status: SalesStatus


class PurchaseOrder(BaseModel):
    id: str
    supplier_id: str
    product_id: str
    quantity: int
    unit_price: float
    order_date: date
    expected_delivery: date
    actual_delivery: date | None = None
    status: PurchaseOrderStatus
    reason: str = ""
    created_by: str  # username


class Approval(BaseModel):
    id: str
    purchase_order_id: str
    requested_by: str  # username
    requested_at: datetime
    reason: str = ""
    status: ApprovalStatus
    decided_by: str | None = None
    decided_at: datetime | None = None
    comment: str | None = None


class AuditLog(BaseModel):
    id: str
    timestamp: datetime
    user_id: str
    username: str
    action: str
    entity: str
    entity_id: str
    status: AuditStatus
    description: str
