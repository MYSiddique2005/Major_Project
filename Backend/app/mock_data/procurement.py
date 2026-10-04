from datetime import timedelta

from app.mock_data import REFERENCE_DATE
from app.mock_data.products import PRODUCTS

_UNIT_COST = {p["id"]: p["unit_cost"] for p in PRODUCTS}

# (supplier, product, qty, ordered N days ago, quoted lead time in days,
#  days late (None = not delivered yet), status, reason)
_ROWS = [
    ("S001", "P001", 400, 170, 6, 0, "Delivered", "Quarterly replenishment"),
    ("S002", "P005", 300, 160, 9, 1, "Delivered", "Quarterly replenishment"),
    ("S003", "P011", 2000, 150, 7, 0, "Delivered", "Bulk cable restock"),
    ("S005", "P004", 350, 140, 8, 1, "Delivered", "Quarterly replenishment"),
    ("S002", "P006", 800, 120, 9, 2, "Delivered", "Stock below reorder level"),
    ("S006", "P012", 250, 110, 9, 0, "Delivered", "Stock below reorder level"),
    ("S007", "P015", 300, 100, 10, 2, "Delivered", "Toner demand from printer rollout"),
    ("S001", "P002", 300, 90, 6, 0, "Delivered", "Quarterly replenishment"),
    ("S002", "P007", 120, 75, 9, 4, "Delivered", "Stock below reorder level"),
    ("S008", "P016", 200, 70, 6, 0, "Delivered", "Quarterly replenishment"),
    ("S004", "P019", 100, 60, 5, 0, "Delivered", "Customer project order"),
    ("S002", "P008", 250, 50, 9, 6, "Delivered", "Stock below reorder level"),
    ("S001", "P001", 300, 45, 6, 1, "Delivered", "Rising laptop demand"),
    ("S009", "P018", 60, 40, 12, 3, "Delivered", "Stock below reorder level"),
    ("S002", "P006", 500, 30, 9, None, "Cancelled", "Duplicate of earlier order"),
    ("S005", "P007", 400, 20, 8, None, "Rejected", "Trial order from alternate supplier"),
    ("S002", "P005", 300, 16, 9, None, "Ordered", "Stock below safety level"),
    ("S006", "P012", 300, 6, 9, None, "Ordered", "Out of stock"),
    ("S003", "P009", 150, 5, 7, None, "Ordered", "Stock below reorder level"),
    ("S007", "P015", 350, 4, 10, None, "Ordered", "Stock below safety level"),
    ("S005", "P003", 120, 3, 8, None, "Approved", "Stock below reorder level"),
    ("S004", "P020", 40, 2, 5, None, "Approved", "Stock below reorder level"),
    ("S001", "P001", 800, 1, 6, None, "Pending Approval", "Stock below safety level and demand rising"),
    ("S002", "P007", 150, 1, 9, None, "Pending Approval", "Stock at critical level"),
    ("S009", "P018", 80, 0, 12, None, "Pending Approval", "Stock below reorder level"),
    ("S008", "P016", 150, 0, 6, None, "Draft", "Stock below reorder level"),
    ("S003", "P010", 50, 0, 7, None, "Draft", "Planned network refresh project"),
]


def _build() -> list[dict]:
    orders = []
    for i, (sid, pid, qty, days_ago, lead, late, status, reason) in enumerate(_ROWS, start=1001):
        order_date = REFERENCE_DATE - timedelta(days=days_ago)
        expected = order_date + timedelta(days=lead)
        orders.append({
            "id": f"PO-{i}", "supplier_id": sid, "product_id": pid, "quantity": qty,
            "unit_price": _UNIT_COST[pid], "order_date": order_date, "expected_delivery": expected,
            "actual_delivery": expected + timedelta(days=late) if late is not None else None,
            "status": status, "reason": reason, "created_by": "procurement",
        })
    return orders


PURCHASE_ORDERS = _build()
