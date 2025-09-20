import sys
import os

# Ensure project root is on sys.path so tests can import the `app` package
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure tests start with a fresh SQLite DB so SQLAlchemy create_all() picks up schema changes
DB_PATH = os.path.join(ROOT, "ecommerce.db")
if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
    except Exception:
        # If removal fails, tests can still proceed but may hit old schema errors
        pass
