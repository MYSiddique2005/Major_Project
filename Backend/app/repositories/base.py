"""Repository abstractions.

Services depend only on these interfaces. Two implementations exist and are
chosen in app/api/deps.py by the DATA_BACKEND setting: PostgreSQL
(postgres.py) and in-memory (mock_*.py, used by the fast test suite and for
running without a database).
"""
import re
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.models.entities import (
    AiInsight,
    AiScan,
    Approval,
    AuditLog,
    InventoryRecord,
    Product,
    PurchaseOrder,
    SalesOrder,
    Supplier,
    User,
)

T = TypeVar("T", bound=BaseModel)


class Repository(ABC, Generic[T]):
    @abstractmethod
    def list(self) -> list[T]: ...

    @abstractmethod
    def get(self, entity_id: str) -> T | None: ...

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def update(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity_id: str) -> bool: ...

    @abstractmethod
    def next_id(self) -> str:
        """Identifier for a new entity (backed by a database sequence in PostgreSQL)."""


class UnitOfWork(ABC):
    """Transaction boundary. Services call commit() once at the end of a use case."""

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


class NoOpUnitOfWork(UnitOfWork):
    """For the in-memory repositories, which apply changes immediately."""

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class ProductRepository(Repository[Product]): ...


class SupplierRepository(Repository[Supplier]): ...


class SalesRepository(Repository[SalesOrder]): ...


class PurchaseOrderRepository(Repository[PurchaseOrder]): ...


class AuditLogRepository(Repository[AuditLog]): ...


class AiScanRepository(Repository[AiScan]): ...


class AiInsightRepository(Repository[AiInsight]): ...


class InventoryRepository(Repository[InventoryRecord]):
    @abstractmethod
    def list_by_product(self, product_id: str) -> list[InventoryRecord]: ...


class ApprovalRepository(Repository[Approval]):
    @abstractmethod
    def get_pending_for_purchase_order(self, purchase_order_id: str) -> Approval | None: ...


class UserRepository(Repository[User]):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...


class InMemoryRepository(Repository[T]):
    """Dict-backed store. Returns copies so callers must call update() to persist,
    which is the same discipline a database-backed repository will require."""

    def __init__(self, model: type[T], seed: list[dict], id_prefix: str, id_width: int = 4):
        self._items: dict[str, T] = {}
        for row in seed:
            item = model.model_validate(row)
            self._items[item.id] = item  # type: ignore[attr-defined]
        self._id_prefix = id_prefix
        self._id_width = id_width
        numbers = [int(m.group()) for key in self._items if (m := re.search(r"\d+$", key))]
        self._sequence = max(numbers, default=0)

    def list(self) -> list[T]:
        return [item.model_copy(deep=True) for item in self._items.values()]

    def get(self, entity_id: str) -> T | None:
        item = self._items.get(entity_id)
        return item.model_copy(deep=True) if item else None

    def add(self, entity: T) -> T:
        self._items[entity.id] = entity.model_copy(deep=True)  # type: ignore[attr-defined]
        return entity

    def update(self, entity: T) -> T:
        if entity.id not in self._items:  # type: ignore[attr-defined]
            raise KeyError(entity.id)  # type: ignore[attr-defined]
        self._items[entity.id] = entity.model_copy(deep=True)  # type: ignore[attr-defined]
        return entity

    def delete(self, entity_id: str) -> bool:
        return self._items.pop(entity_id, None) is not None

    def next_id(self) -> str:
        self._sequence += 1
        return f"{self._id_prefix}{self._sequence:0{self._id_width}d}"
