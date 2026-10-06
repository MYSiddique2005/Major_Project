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
    InsightStatus,
    PurchaseOrderOrigin,
    RiskLevel,
    ScanStatus,
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
    origin: PurchaseOrderOrigin = PurchaseOrderOrigin.MANUAL
    origin_ref: str | None = None  # the insight an AI Insight draft came from
    ai_recommendation: dict | None = None  # the recommendation and its checks, as they stood when drafted


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


class AiScan(BaseModel):
    """One proactive scan of the ERP data by the AI assistant."""

    id: str
    started_at: datetime
    finished_at: datetime | None = None
    trigger: str  # "schedule" or the username that asked for it
    status: ScanStatus
    findings: int = 0  # high and critical findings the analytics raised
    insights: int = 0  # insights the model recorded and the checks accepted
    message: str = ""
    provider: str | None = None
    model: str | None = None


class AiInsight(BaseModel):
    """A finding the AI assistant raised on its own, with its recommendation and the checks made on it."""

    id: str
    scan_id: str
    created_at: datetime
    subject_type: str  # product | supplier
    subject_id: str
    subject_name: str
    severity: RiskLevel  # from the analytics, not from the model
    headline: str
    explanation: str
    action: str
    product_id: str | None = None
    product_name: str | None = None
    supplier_id: str | None = None
    supplier_name: str | None = None
    quantity: int | None = None
    system_quantity: int | None = None
    evidence: list[dict]
    checks: dict
    status: InsightStatus = InsightStatus.NEW
    purchase_order_id: str | None = None  # the draft created from this insight, if any
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
