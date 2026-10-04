"""Loads the demo dataset into PostgreSQL.

    python -m app.db.seed           # seed an empty database (run `alembic upgrade head` first)
    python -m app.db.seed --reset   # wipe all rows and re-seed

The records are the same ones the in-memory backend uses (app/mock_data).
"""
import argparse
import re

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.security import hash_password
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
    supplier_products,
)
from app.db.session import get_session_factory
from app.mock_data.approvals import APPROVALS
from app.mock_data.audit_logs import AUDIT_LOGS
from app.mock_data.inventory import INVENTORY
from app.mock_data.procurement import PURCHASE_ORDERS
from app.mock_data.products import PRODUCTS
from app.mock_data.sales import SALES
from app.mock_data.suppliers import SUPPLIERS
from app.mock_data.users import USERS
from app.models import entities


def _rows(model, entity, records: list[dict], exclude: set[str] | None = None) -> list:
    """Validates each seed record through its domain entity before building the ORM row."""
    return [model(**entity.model_validate(record).model_dump(exclude=exclude)) for record in records]


def is_seeded(session: Session) -> bool:
    return session.scalar(select(func.count()).select_from(UserModel)) > 0


def seed(session: Session) -> None:
    users = [
        {**{k: v for k, v in user.items() if k != "password"}, "hashed_password": hash_password(user["password"])}
        for user in USERS
    ]
    # Insert in foreign-key order.
    for rows in (
        _rows(UserModel, entities.User, users),
        _rows(SupplierModel, entities.Supplier, SUPPLIERS, exclude={"product_ids"}),
        _rows(ProductModel, entities.Product, PRODUCTS),
        _rows(InventoryModel, entities.InventoryRecord, INVENTORY),
        _rows(SalesOrderModel, entities.SalesOrder, SALES),
        _rows(PurchaseOrderModel, entities.PurchaseOrder, PURCHASE_ORDERS),
        _rows(ApprovalModel, entities.Approval, APPROVALS),
        _rows(AuditLogModel, entities.AuditLog, AUDIT_LOGS),
    ):
        session.add_all(rows)
        session.flush()

    session.execute(
        supplier_products.insert(),
        [{"supplier_id": s["id"], "product_id": pid} for s in SUPPLIERS for pid in s["product_ids"]],
    )

    # Continue each ID sequence after the highest seeded ID.
    for table, sequence in SEQUENCES.items():
        ids = session.scalars(select(Base.metadata.tables[table].c.id)).all()
        highest = max((int(m.group()) for i in ids if (m := re.search(r"\d+$", i))), default=0)
        session.execute(text("SELECT setval(:sequence, :value)"), {"sequence": sequence, "value": max(highest, 1)})


def reset(session: Session) -> None:
    """Deletes every row and seeds again. Destructive."""
    tables = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    session.execute(text(f"TRUNCATE {tables} CASCADE"))
    seed(session)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the IntelliERP database with demo data.")
    parser.add_argument("--reset", action="store_true", help="delete all existing rows first")
    args = parser.parse_args()

    with get_session_factory()() as session:
        if args.reset:
            reset(session)
            print("Database reset and seeded.")
        elif is_seeded(session):
            print("Database already contains data; nothing done. Use --reset to wipe and re-seed.")
            return
        else:
            seed(session)
            print("Database seeded.")
        session.commit()


if __name__ == "__main__":
    main()
