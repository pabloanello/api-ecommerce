from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_product_crud():
    # create product
    p = {"title":"Test Product","description":"x","price":9.99,"inventory":10}
    r = client.post("/products/", json=p)
    assert r.status_code == 200
    prod = r.json()
    assert prod["id"]

    # list
    r2 = client.get("/products/")
    assert r2.status_code == 200
    lst = r2.json()
    assert any(x["title"] == "Test Product" for x in lst)

    # get
    r3 = client.get(f"/products/{prod['id']}")
    assert r3.status_code == 200

    # update
    p2 = {"title":"Test Product","description":"y","price":10.0,"inventory":5}
    r4 = client.put(f"/products/{prod['id']}", json=p2)
    assert r4.status_code == 200
    assert r4.json()["price"] == 10.0

    # delete
    r5 = client.delete(f"/products/{prod['id']}")
    assert r5.status_code == 200
    assert r5.json().get("ok") is True
