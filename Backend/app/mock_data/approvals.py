"""Approval records derived from the seeded purchase orders, so the two stay consistent."""
from datetime import datetime, time, timedelta

from app.mock_data.procurement import PURCHASE_ORDERS

_DECIDED = {"Approved", "Ordered", "Delivered"}


def _build() -> list[dict]:
    approvals = []
    for po in PURCHASE_ORDERS:
        if po["status"] in ("Draft", "Cancelled"):
            continue
        requested_at = datetime.combine(po["order_date"], time(10, 15))
        approval = {
            "id": f"APR-{len(approvals) + 1:04d}", "purchase_order_id": po["id"],
            "requested_by": po["created_by"], "requested_at": requested_at, "reason": po["reason"],
            "status": "Pending", "decided_by": None, "decided_at": None, "comment": None,
        }
        if po["status"] in _DECIDED:
            approval.update(status="Approved", decided_by="admin", decided_at=requested_at + timedelta(hours=4))
        elif po["status"] == "Rejected":
            approval.update(status="Rejected", decided_by="admin", decided_at=requested_at + timedelta(hours=5),
                            comment="Quantity exceeds the quarterly budget for this category.")
        approvals.append(approval)
    return approvals


APPROVALS = _build()
