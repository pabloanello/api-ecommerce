import sys
import os

# Ensure project root is on sys.path so this script can import the `app` package
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_user_and_token():
    email = "dbg+user@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "secret"})
    print("register:", r.status_code, r.text)
    if r.status_code == 200:
        return r.json().get("access_token")
    # if user exists, try to fetch token via /auth/token
    rt = client.post("/auth/token", data={"username": email, "password": "secret"})
    print("token:", rt.status_code, rt.text)
    if rt.status_code == 200:
        return rt.json().get("access_token")
    return None


def run():
    token = create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    p = {"title": "DebugProd", "description": "x", "price": 5.0, "inventory": 3}
    r = client.post("/products/", json=p)
    print("create product:", r.status_code, r.text)
    prod = r.json()

    order = {"items": [{"product_id": prod["id"], "quantity": 2}]}
    try:
        r2 = client.post("/orders/", json=order, headers=headers)
        print("create order status:", r2.status_code)
        print("response text:", r2.text)
        try:
            print("json():", r2.json())
        except Exception as e:
            print("json() error:", e)
    except Exception as exc:
        print("request raised exception:", type(exc), exc)


if __name__ == '__main__':
    run()
