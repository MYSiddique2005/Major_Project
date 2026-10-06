import pytest

from tests.conftest import API


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_available(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200


def test_login_success_returns_token_and_permissions(client):
    response = client.post(f"{API}/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["role"] == "ADMIN"
    assert "audit:view" in body["user"]["permissions"]


def test_login_wrong_password(client):
    response = client.post(f"{API}/auth/login", json={"username": "admin", "password": "nope"})
    assert response.status_code == 401


def test_me(client, auth):
    response = client.get(f"{API}/auth/me", headers=auth("inventory"))
    assert response.status_code == 200
    assert response.json()["role"] == "INVENTORY_MANAGER"


@pytest.mark.parametrize("path", ["/products", "/inventory", "/sales", "/suppliers", "/procurement", "/approvals"])
def test_list_endpoints(client, auth, path):
    response = client.get(f"{API}{path}", headers=auth("admin"))
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.parametrize(
    "path",
    ["/dashboard/summary", "/dashboard/sales-trend", "/dashboard/inventory-status", "/dashboard/procurement-status",
     "/sales/stats", "/inventory/stats", "/analytics/alerts", "/audit-logs", "/system/info"],
)
def test_aggregate_endpoints(client, auth, path):
    assert client.get(f"{API}{path}", headers=auth("admin")).status_code == 200


def test_detail_and_not_found(client, auth):
    headers = auth("admin")
    assert client.get(f"{API}/products/P001", headers=headers).json()["name"] == "Laptop Pro 14"
    assert client.get(f"{API}/products/P999", headers=headers).status_code == 404
    assert client.get(f"{API}/sales/SO-9999", headers=headers).status_code == 404


def test_cross_module_relationships(client, auth):
    headers = auth("admin")
    product = client.get(f"{API}/products/P001", headers=headers).json()
    stock = client.get(f"{API}/inventory", params={"product_id": "P001"}, headers=headers).json()
    sales = client.get(f"{API}/sales", params={"product_id": "P001"}, headers=headers).json()
    orders = client.get(f"{API}/procurement", params={"product_id": "P001"}, headers=headers).json()
    supplier = client.get(f"{API}/suppliers/{product['supplier_id']}", headers=headers).json()

    assert product["current_stock"] == sum(r["current_stock"] for r in stock)
    assert sales and orders
    assert "P001" in [p["id"] for p in supplier["products_supplied"]]


def test_inventory_status_rules(client, auth):
    items = client.get(f"{API}/inventory", headers=auth("admin")).json()
    for item in items:
        stock, safety, reorder = item["current_stock"], item["safety_stock"], item["reorder_level"]
        if stock == 0:
            expected = "Out of Stock"
        elif stock <= safety * 0.5:
            expected = "Critical"
        elif stock <= reorder:
            expected = "Low Stock"
        else:
            expected = "In Stock"
        assert item["status"] == expected, item["id"]


def test_filters(client, auth):
    headers = auth("admin")
    critical = client.get(f"{API}/inventory", params={"status": "Critical"}, headers=headers).json()
    assert critical and all(i["status"] == "Critical" for i in critical)
    found = client.get(f"{API}/products", params={"search": "laptop"}, headers=headers).json()
    assert found and all("laptop" in p["name"].lower() for p in found)
