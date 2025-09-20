import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] in ("Hello, world!",)
