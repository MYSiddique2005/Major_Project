"""PostgreSQL implementations of the repository interfaces (SQLAlchemy).

Repositories flush but never commit: the service that owns the use case
commits once through the UnitOfWork, so a workflow step and its audit event
are stored together or not at all.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    SEQUENCES,
    ApprovalModel,
    AuditLogModel,
    InventoryModel,
    ProductModel,
    PurchaseOrderModel,
    SalesOrderModel,
    SupplierModel,
    UserModel,
)
from app.models.entities import (
    Approval,
    AuditLog,
    InventoryRecord,
    Product,
    PurchaseOrder,
    SalesOrder,
    Supplier,
    User,
)
from app.models.enums import ApprovalStatus
from app.repositories.base import (
    ApprovalRepository,
    AuditLogRepository,
    InventoryRepository,
    ProductRepository,
    PurchaseOrderRepository,
    Repository,
    SalesRepository,
    SupplierRepository,
    UnitOfWork,
    UserRepository,
)

T = TypeVar("T", bound=BaseModel)
M = TypeVar("M", bound=Base)


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


class SqlRepository(Repository[T], Generic[T, M]):
    entity: type[T]
    model: type[M]
    id_prefix: str
    id_width: int = 4

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, row: M) -> T:
        return self.entity.model_validate(row, from_attributes=True)

    def _apply(self, row: M, entity: T) -> None:
        for field, value in entity.model_dump().items():
            setattr(row, field, value)

    def list(self) -> list[T]:
        rows = self._session.scalars(select(self.model).order_by(self.model.id)).all()
        return [self._to_entity(row) for row in rows]

    def get(self, entity_id: str) -> T | None:
        row = self._session.get(self.model, entity_id)
        return self._to_entity(row) if row else None

    def add(self, entity: T) -> T:
        row = self.model()
        self._apply(row, entity)
        self._session.add(row)
        self._session.flush()
        return entity

    def update(self, entity: T) -> T:
        row = self._session.get(self.model, entity.id)  # type: ignore[attr-defined]
        if row is None:
            raise KeyError(entity.id)  # type: ignore[attr-defined]
        self._apply(row, entity)
        self._session.flush()
        return entity

    def delete(self, entity_id: str) -> bool:
        row = self._session.get(self.model, entity_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True

    def next_id(self) -> str:
        number = self._session.scalar(select(Sequence(SEQUENCES[self.model.__tablename__]).next_value()))
        return f"{self.id_prefix}{number:0{self.id_width}d}"


class PostgresProductRepository(SqlRepository[Product, ProductModel], ProductRepository):
    entity, model, id_prefix, id_width = Product, ProductModel, "P", 3


class PostgresSalesRepository(SqlRepository[SalesOrder, SalesOrderModel], SalesRepository):
    entity, model, id_prefix = SalesOrder, SalesOrderModel, "SO-"


class PostgresPurchaseOrderRepository(SqlRepository[PurchaseOrder, PurchaseOrderModel], PurchaseOrderRepository):
    entity, model, id_prefix = PurchaseOrder, PurchaseOrderModel, "PO-"


class PostgresAuditLogRepository(SqlRepository[AuditLog, AuditLogModel], AuditLogRepository):
    entity, model, id_prefix, id_width = AuditLog, AuditLogModel, "AUD-", 5


class PostgresSupplierRepository(SqlRepository[Supplier, SupplierModel], SupplierRepository):
    entity, model, id_prefix, id_width = Supplier, SupplierModel, "S", 3

    def _apply(self, row: SupplierModel, entity: Supplier) -> None:
        for field, value in entity.model_dump(exclude={"product_ids"}).items():
            setattr(row, field, value)
        row.supplied_products = [p for pid in entity.product_ids if (p := self._session.get(ProductModel, pid))]


class PostgresInventoryRepository(SqlRepository[InventoryRecord, InventoryModel], InventoryRepository):
    entity, model, id_prefix, id_width = InventoryRecord, InventoryModel, "INV-", 3

    def list_by_product(self, product_id: str) -> list[InventoryRecord]:
        rows = self._session.scalars(
            select(InventoryModel).where(InventoryModel.product_id == product_id).order_by(InventoryModel.id)
        ).all()
        return [self._to_entity(row) for row in rows]


class PostgresApprovalRepository(SqlRepository[Approval, ApprovalModel], ApprovalRepository):
    entity, model, id_prefix = Approval, ApprovalModel, "APR-"

    def get_pending_for_purchase_order(self, purchase_order_id: str) -> Approval | None:
        row = self._session.scalars(
            select(ApprovalModel).where(
                ApprovalModel.purchase_order_id == purchase_order_id,
                ApprovalModel.status == ApprovalStatus.PENDING,
            )
        ).first()
        return self._to_entity(row) if row else None


class PostgresUserRepository(SqlRepository[User, UserModel], UserRepository):
    entity, model, id_prefix, id_width = User, UserModel, "U", 3

    def get_by_username(self, username: str) -> User | None:
        row = self._session.scalars(select(UserModel).where(UserModel.username == username)).first()
        return self._to_entity(row) if row else None
