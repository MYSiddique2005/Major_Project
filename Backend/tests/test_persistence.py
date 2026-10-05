"""PostgreSQL-only checks: skipped unless TEST_DATABASE_URL is set."""
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from tests.conftest import API, requires_postgres

pytestmark = requires_postgres


def _session():
    from app.db.session import get_session_factory

    return get_session_factory()()


def test_health_reports_database(client):
    body = client.get("/health").json()
    assert body["data_backend"] == "postgres"
    assert body["database"] == "ok"


def test_workflow_is_stored_in_the_database(client, auth):
    from app.db.models import ApprovalModel, AuditLogModel, PurchaseOrderModel

    headers = auth("procurement")
    po_id = client.post(
        f"{API}/procurement", json={"supplier_id": "S001", "product_id": "P001", "quantity": 10}, headers=headers
    ).json()["id"]
    client.post(f"{API}/procurement/{po_id}/submit", headers=headers)

    # Read back through a brand-new session, bypassing the application.
    with _session() as session:
        po = session.get(PurchaseOrderModel, po_id)
        assert po is not None and po.status == "Pending Approval"
        approval = session.scalars(select(ApprovalModel).where(ApprovalModel.purchase_order_id == po_id)).one()
        assert approval.status == "Pending"
        actions = session.scalars(select(AuditLogModel.action).where(AuditLogModel.entity_id == po_id)).all()
        assert set(actions) == {"CREATE_PURCHASE_ORDER", "SUBMIT_FOR_APPROVAL"}


def test_new_ids_continue_after_seed_data(client, auth):
    headers = auth("procurement")
    body = {"supplier_id": "S001", "product_id": "P001", "quantity": 1}
    first = client.post(f"{API}/procurement", json=body, headers=headers).json()["id"]
    second = client.post(f"{API}/procurement", json=body, headers=headers).json()["id"]
    assert (first, second) == ("PO-1028", "PO-1029")


def test_rejected_request_leaves_no_rows(client, auth):
    from app.db.models import PurchaseOrderModel

    with _session() as session:
        before = len(session.scalars(select(PurchaseOrderModel.id)).all())
    response = client.post(
        f"{API}/procurement", json={"supplier_id": "S004", "product_id": "P001", "quantity": 5}, headers=auth("admin")
    )
    assert response.status_code == 400
    with _session() as session:
        assert len(session.scalars(select(PurchaseOrderModel.id)).all()) == before


def test_failed_login_audit_is_committed(client):
    from app.db.models import AuditLogModel

    client.post(f"{API}/auth/login", json={"username": "admin", "password": "wrong"})
    with _session() as session:
        failed = session.scalars(
            select(AuditLogModel).where(AuditLogModel.status == "FAILED", AuditLogModel.username == "admin")
        ).all()
        assert len(failed) == 1


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE purchase_orders SET status = 'Shipped' WHERE id = 'PO-1001'",  # not a valid status
        "UPDATE purchase_orders SET quantity = 0 WHERE id = 'PO-1001'",
        "UPDATE inventory SET current_stock = -1 WHERE id = 'INV-001'",
        "UPDATE products SET supplier_id = 'S999' WHERE id = 'P001'",  # unknown supplier
        "DELETE FROM products WHERE id = 'P001'",  # still referenced by inventory, sales, purchase orders
    ],
)
def test_database_constraints_reject_invalid_data(client, statement):
    with _session() as session, pytest.raises(IntegrityError):
        session.execute(text(statement))


def test_dataset_loader_moves_history_to_today(client, auth):
    from datetime import date

    from app.db.load_dataset import DEFAULT_DATA_DIR, load
    from app.db.models import PurchaseOrderModel, SalesOrderModel
    from app.db.seed import clear

    if not DEFAULT_DATA_DIR.exists():
        pytest.skip("Data/processed/erp has not been built")

    today = date.today()
    with _session() as session:
        clear(session)
        counts = load(session, DEFAULT_DATA_DIR, months=1, today=today)
        session.commit()
        order_dates = session.scalars(select(SalesOrderModel.order_date)).all()
        open_orders = session.scalars(
            select(PurchaseOrderModel).where(PurchaseOrderModel.actual_delivery.is_(None))
        ).all()

    assert counts["products"] == 227 and counts["suppliers"] == 7
    assert max(order_dates) == today and (today - min(order_dates)).days < 31
    assert open_orders and all(po.status == "Ordered" for po in open_orders)

    headers = auth("admin")
    assert client.get(f"{API}/dashboard/summary", headers=headers).json()["total_orders"] == counts["sales_orders"]
    assert len(client.get(f"{API}/analytics/stock-risk", headers=headers).json()) == 227
    # New purchase orders continue after the loaded IDs.
    draft = client.post(
        f"{API}/procurement", json={"supplier_id": "S004", "product_id": "P100", "quantity": 12}, headers=auth("procurement")
    )
    assert draft.status_code == 201, draft.text
