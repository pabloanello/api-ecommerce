from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4
import pytest
from fastapi import HTTPException
from jose import jwt
from unittest.mock import MagicMock, patch
from app.auth import get_current_user, SECRET_KEY, ALGORITHM

client = TestClient(app)


class DummyUser:
    def __init__(self, email):
        self.email = email


class DummyDB:
    def __init__(self, user=None):
        self._user = user

    def query(self, model):
        class Query:
            def __init__(self, user):
                self._user = user

            def filter(self, *args, **kwargs):
                class Filter:
                    def __init__(self, user):
                        self._user = user

                    def first(self):
                        return self._user

                return Filter(self._user)

        return Query(self._user)


def create_token(email):
    return jwt.encode({"sub": email}, SECRET_KEY, algorithm=ALGORITHM)


def test_register_and_login():
    # use a unique email to avoid conflicts with persisted DB
    email = f"bob+{uuid4().hex}@example.com"

    # Register
    r = client.post("/auth/register", json={"email": email, "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data

    # Login
    r2 = client.post("/auth/token", data={"username": email, "password": "secret"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert "access_token" in data2


def test_get_current_user_valid():
    user = DummyUser(email="test@example.com")
    db = DummyDB(user)
    token = create_token(user.email)
    # Patch Depends to pass our dummy db
    with patch("app.db.deps.get_db", return_value=db):
        result = get_current_user(token=token, db=db)
        assert result.email == user.email


def test_get_current_user_invalid_token():
    db = DummyDB(None)
    invalid_token = "invalid.token.value"
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=invalid_token, db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"


def test_get_current_user_user_not_found():
    db = DummyDB(None)
    token = create_token("notfound@example.com")
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
