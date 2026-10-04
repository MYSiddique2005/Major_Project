from tests.conftest import API

NEW_PO = {"supplier_id": "S001", "product_id": "P001", "quantity": 100}


def test_unauthenticated_request_is_rejected(client):
    assert client.get(f"{API}/products").status_code == 401


def test_invalid_token_is_rejected(client):
    assert client.get(f"{API}/products", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


def test_employee_has_read_only_access(client, auth):
    headers = auth("employee")
    assert client.get(f"{API}/products", headers=headers).status_code == 200
    assert client.get(f"{API}/inventory", headers=headers).status_code == 200
    assert client.get(f"{API}/procurement", headers=headers).status_code == 403
    assert client.post(f"{API}/procurement", json=NEW_PO, headers=headers).status_code == 403
    assert client.get(f"{API}/audit-logs", headers=headers).status_code == 403
    assert client.post(f"{API}/ai/chat", json={"message": "hi"}, headers=headers).status_code == 403


def test_inventory_manager_cannot_create_or_approve(client, auth):
    headers = auth("inventory")
    assert client.get(f"{API}/sales", headers=headers).status_code == 200
    assert client.post(f"{API}/procurement", json=NEW_PO, headers=headers).status_code == 403
    assert client.get(f"{API}/approvals", headers=headers).status_code == 403
    assert client.post(f"{API}/approvals/APR-0001/approve", headers=headers).status_code == 403


def test_procurement_manager_scope(client, auth):
    headers = auth("procurement")
    assert client.get(f"{API}/procurement", headers=headers).status_code == 200
    assert client.get(f"{API}/approvals", headers=headers).status_code == 200
    assert client.get(f"{API}/sales", headers=headers).status_code == 403
    assert client.get(f"{API}/audit-logs", headers=headers).status_code == 403


def test_admin_can_view_audit_logs(client, auth):
    assert client.get(f"{API}/audit-logs", headers=auth("admin")).status_code == 200
