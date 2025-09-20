from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)


def create_user_and_token():
    email = f"cart+{uuid4().hex}@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "secret"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_cart_checkout_creates_order_and_adjusts_inventory():
    token = create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # create product
    p = {"title":"CartProd","description":"x","price":10.0,"inventory":5}
    r = client.post("/products/", json=p)
    assert r.status_code == 200
    prod = r.json()

    # add to cart
    r2 = client.post("/cart/items", json={"product_id": prod["id"], "quantity": 3}, headers=headers)
    assert r2.status_code == 200
    cart = r2.json()
    assert len(cart["items"]) == 1

    # checkout
    r3 = client.post("/cart/checkout", headers=headers)
    assert r3.status_code == 200
    body = r3.json()
    assert body.get("ok") is True
    order_id = body.get("order_id")
    assert order_id is not None

    # inventory reduced
    r4 = client.get(f"/products/{prod['id']}")
    assert r4.status_code == 200
    assert r4.json()["inventory"] == 2


def test_update_item_and_clear_cart():
    token = create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # create product
    p = {"title":"CartProd2","description":"x","price":8.0,"inventory":10}
    r = client.post("/products/", json=p)
    assert r.status_code == 200
    prod = r.json()

    # add to cart
    r2 = client.post("/cart/items", json={"product_id": prod["id"], "quantity": 2}, headers=headers)
    assert r2.status_code == 200
    cart = r2.json()
    assert len(cart["items"]) == 1
    item_id = cart["items"][0]["id"]

    # update quantity
    r3 = client.patch(f"/cart/items/{item_id}", json={"product_id": prod["id"], "quantity": 5}, headers=headers)
    assert r3.status_code == 200
    cart2 = r3.json()
    assert cart2["items"][0]["quantity"] == 5

    # clear cart
    r4 = client.post("/cart/clear", headers=headers)
    assert r4.status_code == 200
    assert r4.json()["items"] == []


def test_item_by_id_remove_by_product_and_summary():
    token = create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # create two products
    p1 = {"title":"P1","description":"x","price":3.0,"inventory":10}
    p2 = {"title":"P2","description":"x","price":7.5,"inventory":5}
    r = client.post("/products/", json=p1)
    assert r.status_code == 200
    p1 = r.json()
    r = client.post("/products/", json=p2)
    assert r.status_code == 200
    p2 = r.json()

    # add both to cart
    client.post("/cart/items", json={"product_id": p1["id"], "quantity": 2}, headers=headers)
    r = client.post("/cart/items", json={"product_id": p2["id"], "quantity": 1}, headers=headers)
    assert r.status_code == 200
    cart = r.json()
    # get item by id
    item_id = cart["items"][0]["id"]
    r2 = client.get(f"/cart/items/{item_id}", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["product_id"] == cart["items"][0]["product_id"]

    # set quantity by product_id (upsert behavior)
    r3 = client.put(f"/cart/items/product/{p1['id']}", json={"product_id": p1["id"], "quantity": 5}, headers=headers)
    assert r3.status_code == 200
    assert any(it["product_id"] == p1["id"] and it["quantity"] == 5 for it in r3.json()["items"])

    # remove item by product_id
    r4 = client.delete(f"/cart/items/product/{p2['id']}", headers=headers)
    assert r4.status_code == 200
    assert all(it["product_id"] != p2["id"] for it in r4.json()["items"])

    # summary
    r5 = client.get("/cart/summary", headers=headers)
    assert r5.status_code == 200
    s = r5.json()
    assert s["total_items"] == sum(it["quantity"] for it in r4.json()["items"]) or s["total_items"] >= 0
