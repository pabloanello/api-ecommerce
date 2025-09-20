"""Application package.

Expose the main FastAPI `app` here so tests and runners can import with `from app import app`.
"""

from .main import app  # re-export for convenience

__all__ = ["app"]
