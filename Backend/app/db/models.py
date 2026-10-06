"""SQLAlchemy table definitions.

Each model mirrors a domain entity in app/models/entities.py; repositories
convert between the two so services never see ORM objects. Derived values
(stock status, totals) are still computed in services, not stored.
"""
import enum
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    ApprovalStatus,
    AuditStatus,
    InsightStatus,
    ProductStatus,
    PurchaseOrderOrigin,
    PurchaseOrderStatus,
    RiskLevel,
    Role,
    SalesStatus,
    ScanStatus,
    SupplierStatus,
)

ID = String(16)
Money = Numeric(12, 2, asdecimal=False)

# One sequence per table backs Repository.next_id(); IDs keep their readable prefixes (PO-1028, ...).
SEQUENCES = {
    "users": "user_id_seq",
    "suppliers": "supplier_id_seq",
    "products": "product_id_seq",
    "inventory": "inventory_id_seq",
    "sales_orders": "sales_order_id_seq",
    "purchase_orders": "purchase_order_id_seq",
    "approvals": "approval_id_seq",
    "audit_logs": "audit_log_id_seq",
    "ai_scans": "ai_scan_id_seq",
    "ai_insights": "ai_insight_id_seq",
}


def _enum(enum_class: type[enum.Enum], name: str) -> Enum:
    """Stores the enum's value (e.g. "Pending Approval") in a VARCHAR guarded by a CHECK constraint."""
    return Enum(
        enum_class,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda members: [member.value for member in members],
    )


supplier_products = Table(
    "supplier_products",
    Base.metadata,
    Column("supplier_id", ID, ForeignKey("suppliers.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", ID, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(_enum(Role, "role"))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SupplierModel(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    contact_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(40))
    country: Mapped[str] = mapped_column(String(80))
    avg_delivery_days: Mapped[float] = mapped_column(Float)
    delivery_reliability: Mapped[float] = mapped_column(Float)
    status: Mapped[SupplierStatus] = mapped_column(_enum(SupplierStatus, "status"))

    # Every product this supplier can deliver (a product also names one primary supplier).
    supplied_products: Mapped[list["ProductModel"]] = relationship(
        secondary=supplier_products, order_by="ProductModel.id", lazy="selectin"
    )

    @property
    def product_ids(self) -> list[str]:
        return [product.id for product in self.supplied_products]


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    price: Mapped[float] = mapped_column(Money)
    unit_cost: Mapped[float] = mapped_column(Money)
    status: Mapped[ProductStatus] = mapped_column(_enum(ProductStatus, "status"))


class InventoryModel(Base):
    __tablename__ = "inventory"
    __table_args__ = (CheckConstraint("current_stock >= 0", name="current_stock_non_negative"),)

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    warehouse: Mapped[str] = mapped_column(String(80))
    current_stock: Mapped[int] = mapped_column(Integer)
    safety_stock: Mapped[int] = mapped_column(Integer)
    reorder_level: Mapped[int] = mapped_column(Integer)
    last_updated: Mapped[date] = mapped_column(Date)


class SalesOrderModel(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (CheckConstraint("quantity > 0", name="quantity_positive"),)

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    customer: Mapped[str] = mapped_column(String(160))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Money)
    order_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[SalesStatus] = mapped_column(_enum(SalesStatus, "status"))


class PurchaseOrderModel(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = (CheckConstraint("quantity > 0", name="quantity_positive"),)

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Money)
    order_date: Mapped[date] = mapped_column(Date)
    expected_delivery: Mapped[date] = mapped_column(Date)
    actual_delivery: Mapped[date | None] = mapped_column(Date)
    status: Mapped[PurchaseOrderStatus] = mapped_column(_enum(PurchaseOrderStatus, "status"), index=True)
    reason: Mapped[str] = mapped_column(String(500), default="")
    created_by: Mapped[str] = mapped_column(String(64))
    origin: Mapped[PurchaseOrderOrigin] = mapped_column(
        _enum(PurchaseOrderOrigin, "origin"), default=PurchaseOrderOrigin.MANUAL, server_default="Manual"
    )
    origin_ref: Mapped[str | None] = mapped_column(String(16))
    ai_recommendation: Mapped[dict | None] = mapped_column(JSON)


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    requested_by: Mapped[str] = mapped_column(String(64))
    requested_at: Mapped[datetime] = mapped_column(DateTime)
    reason: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[ApprovalStatus] = mapped_column(_enum(ApprovalStatus, "status"), index=True)
    decided_by: Mapped[str | None] = mapped_column(String(64))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)
    comment: Mapped[str | None] = mapped_column(String(500))


class AuditLogModel(Base):
    """Append-only. No foreign keys: an event must survive even if its subject is deleted,
    and failed logins have no real user."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[str] = mapped_column(String(16))
    username: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(32))
    status: Mapped[AuditStatus] = mapped_column(_enum(AuditStatus, "status"))
    description: Mapped[str] = mapped_column(Text)


class AiScanModel(Base):
    __tablename__ = "ai_scans"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    trigger: Mapped[str] = mapped_column(String(64))
    status: Mapped[ScanStatus] = mapped_column(_enum(ScanStatus, "status"))
    findings: Mapped[int] = mapped_column(Integer, default=0)
    insights: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(500), default="")
    provider: Mapped[str | None] = mapped_column(String(32))
    model: Mapped[str | None] = mapped_column(String(64))


class AiInsightModel(Base):
    """No foreign keys to products or suppliers: an insight is a record of what was said at the time."""

    __tablename__ = "ai_insights"

    id: Mapped[str] = mapped_column(ID, primary_key=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("ai_scans.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    subject_type: Mapped[str] = mapped_column(String(16))
    subject_id: Mapped[str] = mapped_column(String(16), index=True)
    subject_name: Mapped[str] = mapped_column(String(160))
    severity: Mapped[RiskLevel] = mapped_column(_enum(RiskLevel, "severity"))
    headline: Mapped[str] = mapped_column(String(200))
    explanation: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(32))
    product_id: Mapped[str | None] = mapped_column(String(16))
    product_name: Mapped[str | None] = mapped_column(String(160))
    supplier_id: Mapped[str | None] = mapped_column(String(16))
    supplier_name: Mapped[str | None] = mapped_column(String(160))
    quantity: Mapped[int | None] = mapped_column(Integer)
    system_quantity: Mapped[int | None] = mapped_column(Integer)
    evidence: Mapped[list] = mapped_column(JSON)
    checks: Mapped[dict] = mapped_column(JSON)
    status: Mapped[InsightStatus] = mapped_column(_enum(InsightStatus, "status"), index=True)
    purchase_order_id: Mapped[str | None] = mapped_column(String(16))
    reviewed_by: Mapped[str | None] = mapped_column(String(64))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
