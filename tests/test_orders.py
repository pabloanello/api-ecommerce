from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)


def create_user_and_token():
    email = f"ord+{uuid4().hex}@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "secret"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_order_cancel_and_restock():
    token = create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # create product
    p = {"title":"CancelTest","description":"x","price":5.0,"inventory":3}
    r = client.post("/products/", json=p)
    assert r.status_code == 200
    prod = r.json()

    # create order for 2 units
    order = {"items":[{"product_id": prod["id"], "quantity": 2}]}
    r2 = client.post("/orders/", json=order, headers=headers)
    assert r2.status_code == 200
    ord_resp = r2.json()
    oid = ord_resp["id"]

    # inventory should have decreased
    r3 = client.get(f"/products/{prod['id']}")
    assert r3.status_code == 200
    assert r3.json()["inventory"] == 1

    # cancel order
    r4 = client.post(f"/orders/{oid}/cancel", headers=headers)
    assert r4.status_code == 200
    assert r4.json()["ok"] is True

    # inventory should be back to 3
    r5 = client.get(f"/products/{prod['id']}")
    assert r5.status_code == 200
    assert r5.json()["inventory"] == 3
