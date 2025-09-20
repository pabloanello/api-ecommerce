import os
from app.core import config

def test_settings_defaults(monkeypatch):
    # Remove env vars to test defaults
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    s = config.Settings()
    assert s.DATABASE_URL == "sqlite:///./ecommerce.db"
    assert s.SECRET_KEY == "supersecretkey123"
    assert s.ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24

def test_settings_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "envkey")
    s = config.Settings()
    assert s.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert s.SECRET_KEY == "envkey"
