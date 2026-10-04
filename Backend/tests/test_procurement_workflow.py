from tests.conftest import API

NEW_PO = {"supplier_id": "S001", "product_id": "P001", "quantity": 800, "reason": "Replenishment required"}


def _create(client, headers, **overrides):
    return client.post(f"{API}/procurement", json={**NEW_PO, **overrides}, headers=headers)


def _pending_approval_id(client, headers, po_id):
    approvals = client.get(f"{API}/approvals", params={"status": "Pending"}, headers=headers).json()
    return next(a["id"] for a in approvals if a["purchase_order_id"] == po_id)


def _audit_actions(client, auth, po_id):
    logs = client.get(f"{API}/audit-logs", params={"search": po_id}, headers=auth("admin")).json()
    return {log["action"] for log in logs}


def test_create_draft_applies_defaults(client, auth):
    response = _create(client, auth("procurement"))
    assert response.status_code == 201
    po = response.json()
    assert po["status"] == "Draft"
    assert po["unit_price"] == 980.0
    assert po["total_amount"] == 800 * 980.0
    assert po["created_by"] == "procurement"


def test_create_validation(client, auth):
    headers = auth("procurement")
    assert _create(client, headers, quantity=0).status_code == 422
    assert _create(client, headers, supplier_id="S999").status_code == 400
    assert _create(client, headers, supplier_id="S010", product_id="P021").status_code == 400  # inactive supplier
    assert _create(client, headers, supplier_id="S004").status_code == 400  # supplier does not supply product


def test_edit_and_delete_draft(client, auth):
    headers = auth("procurement")
    po_id = _create(client, headers).json()["id"]

    updated = client.put(f"{API}/procurement/{po_id}", json={"quantity": 500}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["quantity"] == 500

    assert client.delete(f"{API}/procurement/{po_id}", headers=headers).status_code == 204
    assert client.get(f"{API}/procurement/{po_id}", headers=headers).status_code == 404


def test_approve_workflow_and_audit_trail(client, auth):
    headers = auth("procurement")
    po_id = _create(client, headers).json()["id"]

    submitted = client.post(f"{API}/procurement/{po_id}/submit", headers=headers)
    assert submitted.json()["status"] == "Pending Approval"
    # Submitted orders are locked.
    assert client.put(f"{API}/procurement/{po_id}", json={"quantity": 1}, headers=headers).status_code == 400
    assert client.delete(f"{API}/procurement/{po_id}", headers=headers).status_code == 400

    approval_id = _pending_approval_id(client, headers, po_id)
    approved = client.post(f"{API}/approvals/{approval_id}/approve", headers=auth("admin"))
    assert approved.status_code == 200
    assert approved.json()["status"] == "Approved"
    assert approved.json()["decided_by"] == "admin"
    assert client.get(f"{API}/procurement/{po_id}", headers=headers).json()["status"] == "Approved"

    # A decision is final.
    assert client.post(f"{API}/approvals/{approval_id}/reject", headers=headers).status_code == 400

    assert {"CREATE_PURCHASE_ORDER", "SUBMIT_FOR_APPROVAL", "APPROVE_PURCHASE_ORDER"} <= _audit_actions(
        client, auth, po_id
    )


def test_reject_workflow(client, auth):
    headers = auth("procurement")
    po_id = _create(client, headers).json()["id"]
    client.post(f"{API}/procurement/{po_id}/submit", headers=headers)

    approval_id = _pending_approval_id(client, headers, po_id)
    rejected = client.post(
        f"{API}/approvals/{approval_id}/reject", json={"comment": "Over budget"}, headers=headers
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "Rejected"
    assert rejected.json()["comment"] == "Over budget"
    assert client.get(f"{API}/procurement/{po_id}", headers=headers).json()["status"] == "Rejected"
    assert "REJECT_PURCHASE_ORDER" in _audit_actions(client, auth, po_id)


def test_login_is_audited(client, auth):
    client.post(f"{API}/auth/login", json={"username": "admin", "password": "wrong"})
    logs = client.get(f"{API}/audit-logs", params={"action": "LOGIN"}, headers=auth("admin")).json()
    assert logs[0]["status"] == "SUCCESS"
    assert any(log["status"] == "FAILED" and log["username"] == "admin" for log in logs)
