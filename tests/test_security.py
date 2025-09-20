import pytest
from app.core import security
from jose import jwt
from datetime import timedelta

class DummyUser:
    def __init__(self, email, hashed_password=None):
        self.email = email
        self.hashed_password = hashed_password

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

def test_verify_password_and_hash():
    password = "secret123"
    hashed = security.get_password_hash(password)
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong", hashed)

def test_create_access_token_and_decode():
    data = {"sub": "test@example.com"}
    token = security.create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded

def test_get_current_active_user_valid():
    user = DummyUser(email="test@example.com")
    db = DummyDB(user)
    token = security.create_access_token({"sub": user.email})
    result = security.get_current_active_user(token=token, db=db)
    assert result.email == user.email

def test_get_current_active_user_invalid_token():
    db = DummyDB(None)
    with pytest.raises(security.HTTPException) as exc:
        security.get_current_active_user(token="invalid.token.value", db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"

def test_get_current_active_user_user_not_found():
    db = DummyDB(None)
    token = security.create_access_token({"sub": "notfound@example.com"})
    with pytest.raises(security.HTTPException) as exc:
        security.get_current_active_user(token=token, db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
