"""Historical audit trail consistent with the seeded purchase orders and approvals."""
from datetime import datetime, time, timedelta

from app.mock_data import REFERENCE_DATE
from app.mock_data.approvals import APPROVALS
from app.mock_data.procurement import PURCHASE_ORDERS
from app.mock_data.users import USERS

_USER_IDS = {u["username"]: u["id"] for u in USERS}
_RECENT_PO_COUNT = 12


def _event(timestamp, username, action, entity, entity_id, description, status="SUCCESS"):
    return {"timestamp": timestamp, "user_id": _USER_IDS.get(username, "unknown"), "username": username,
            "action": action, "entity": entity, "entity_id": entity_id, "status": status,
            "description": description}


def _build() -> list[dict]:
    events = []
    approvals = {a["purchase_order_id"]: a for a in APPROVALS}
    for po in PURCHASE_ORDERS[-_RECENT_PO_COUNT:]:
        created = datetime.combine(po["order_date"], time(9, 40))
        events.append(_event(created, po["created_by"], "CREATE_PURCHASE_ORDER", "Purchase Order", po["id"],
                             f"Created draft for {po['quantity']} x {po['product_id']} from {po['supplier_id']}"))
        approval = approvals.get(po["id"])
        if approval is None:
            continue
        events.append(_event(approval["requested_at"], approval["requested_by"], "SUBMIT_FOR_APPROVAL",
                             "Purchase Order", po["id"], "Submitted for approval"))
        if approval["status"] == "Approved":
            events.append(_event(approval["decided_at"], approval["decided_by"], "APPROVE_PURCHASE_ORDER",
                                 "Purchase Order", po["id"], "Purchase order approved"))
        elif approval["status"] == "Rejected":
            events.append(_event(approval["decided_at"], approval["decided_by"], "REJECT_PURCHASE_ORDER",
                                 "Purchase Order", po["id"], approval["comment"]))

    for days_ago, username in [(6, "admin"), (3, "inventory"), (2, "employee"), (1, "procurement"), (1, "admin")]:
        ts = datetime.combine(REFERENCE_DATE - timedelta(days=days_ago), time(8, 55))
        events.append(_event(ts, username, "LOGIN", "User", _USER_IDS[username], "User logged in"))
    events.append(_event(datetime.combine(REFERENCE_DATE - timedelta(days=2), time(8, 50)), "employee", "LOGIN",
                         "User", _USER_IDS["employee"], "Invalid username or password", status="FAILED"))

    events.sort(key=lambda e: e["timestamp"])
    for i, event in enumerate(events, start=1):
        event["id"] = f"AUD-{i:05d}"
    return events


AUDIT_LOGS = _build()
