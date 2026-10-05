"""Loads the Wide World Importers dataset (Data/processed/erp) into PostgreSQL.

    python -m app.db.load_dataset --reset              # replace all rows with the last 12 months
    python -m app.db.load_dataset --reset --months 6   # a shorter history
    python -m app.db.load_dataset --reset --months 0   # the whole history (2013-2016)

Products, suppliers and stock are loaded in full; sales and purchase orders are limited to the
most recent months because the services read whole tables per request. All dates are moved
forward by the same number of days so that the dataset's last day is today, as the analytics
look at the most recent weeks. Users are the demo accounts; approvals and audit logs start empty.

Sales are real source records; purchase orders and stock levels are simulated from them
(see Data/README.md).
"""
import argparse
import csv
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import (
    InventoryModel,
    ProductModel,
    PurchaseOrderModel,
    SalesOrderModel,
    SupplierModel,
    UserModel,
    supplier_products,
)
from app.db.seed import clear, is_seeded, sync_sequences
from app.db.session import get_session_factory
from app.mock_data.users import USERS
from app.models import entities

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "Data" / "processed" / "erp"
DAYS_PER_MONTH = 365 / 12


def _read(data_dir: Path, name: str) -> list[dict]:
    with open(data_dir / f"{name}.csv", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _records(entity, rows: list[dict], exclude: set[str] | None = None) -> list[dict]:
    """Validates each CSV row through its domain entity; columns the entity does not have are ignored."""
    return [entity.model_validate(row).model_dump(exclude=exclude) for row in rows]


def load(session: Session, data_dir: Path, months: int, today: date) -> dict[str, int]:
    sales = _read(data_dir, "sales_orders")
    purchases = _read(data_dir, "purchase_orders")
    last_day = max(date.fromisoformat(row["order_date"]) for row in sales)
    shift = today - last_day
    first_day = last_day - timedelta(days=round(months * DAYS_PER_MONTH)) if months else date.min

    def moved(value: str) -> date | None:
        return date.fromisoformat(value) + shift if value else None

    sales = [
        {**row, "order_date": moved(row["order_date"])}
        for row in sales
        if date.fromisoformat(row["order_date"]) > first_day
    ]
    purchases = [
        {
            **row,
            "order_date": moved(row["order_date"]),
            "expected_delivery": moved(row["expected_delivery"]),
            "actual_delivery": moved(row["actual_delivery"]),
        }
        for row in purchases
        if date.fromisoformat(row["order_date"]) > first_day
    ]
    inventory = [{**row, "last_updated": moved(row["last_updated"])} for row in _read(data_dir, "inventory")]
    links = _read(data_dir, "supplier_products")
    product_ids: dict[str, list[str]] = {}
    for link in links:
        product_ids.setdefault(link["supplier_id"], []).append(link["product_id"])
    suppliers = [{**row, "product_ids": product_ids.get(row["id"], [])} for row in _read(data_dir, "suppliers")]
    users = [
        {**{k: v for k, v in user.items() if k != "password"}, "hashed_password": hash_password(user["password"])}
        for user in USERS
    ]

    # Insert in foreign-key order.
    tables = [
        (UserModel, _records(entities.User, users)),
        (SupplierModel, _records(entities.Supplier, suppliers, exclude={"product_ids"})),
        (ProductModel, _records(entities.Product, _read(data_dir, "products"))),
        (InventoryModel, _records(entities.InventoryRecord, inventory)),
        (SalesOrderModel, _records(entities.SalesOrder, sales)),
        (PurchaseOrderModel, _records(entities.PurchaseOrder, purchases)),
    ]
    for model, records in tables:
        session.execute(insert(model), records)
    session.execute(supplier_products.insert(), links)
    sync_sequences(session)
    return {model.__tablename__: len(records) for model, records in tables}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the Wide World Importers dataset into the IntelliERP database.")
    parser.add_argument("--reset", action="store_true", help="delete all existing rows first")
    parser.add_argument("--months", type=int, default=12, help="months of sales and purchase history (0 = all)")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="folder with the erp CSV files")
    args = parser.parse_args()

    with get_session_factory()() as session:
        if args.reset:
            clear(session)
        elif is_seeded(session):
            print("Database already contains data; nothing done. Use --reset to replace it.")
            return
        counts = load(session, args.data_dir, args.months, date.today())
        session.commit()
    print("Loaded: " + ", ".join(f"{count:,} {table}" for table, count in counts.items()))


if __name__ == "__main__":
    main()
