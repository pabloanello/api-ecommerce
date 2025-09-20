![Build Status](https://github.com/pabloanello/api-ecommerce/actions/workflows/ci.yml/badge.svg)
![Build Status](https://github.com/pabloanello/api-ecommerce/actions/workflows/deploy.yml/badge.svg)

# FastAPI E-commerce API

Minimal e-commerce REST API built with FastAPI, SQLAlchemy and JWT authentication.

## Standard Project Structure

```text
app/
  __init__.py
  main.py              # FastAPI app instance, middleware, and router includes
  core/
    __init__.py
    config.py          # Settings, environment variables
    security.py        # Auth/JWT/password logic
    utils.py           # Helper functions
  models/
    __init__.py
    user.py
    product.py
    order.py
    cart.py
  schemas/
    __init__.py
    user.py
    product.py
    order.py
    cart.py
    token.py
  api/
    __init__.py
    v1/
      __init__.py
      users.py
      products.py
      orders.py
      cart.py
      auth.py
  db/
    __init__.py
    base.py
    session.py
    deps.py
alembic/
  env.py
  versions/
alembic.ini
requirements.txt
pyproject.toml
Dockerfile
.env                   # Environment variables (never commit secrets)
README.md
README_DEPLOY.md
tests/
  test_auth.py
  test_products.py
  test_orders.py
  test_cart.py
  conftest.py
```

**Key points:**
- Models and schemas are split by feature for maintainability.
- `core/` for settings, security, and utilities.
- `api/v1/` for routers, versioned for future-proofing.
- `db/` for database setup and session management.
- Tests mirror the API structure.
- Root contains deployment/config files.

## Environment Variables
- `DATABASE_URL` (default: `sqlite:///./ecommerce.db`)
- `SECRET_KEY` (default: `supersecretkey123`)
- `PORT` (default: 8080, for Docker/Cloud Run)

## Alembic Migrations
```bash
pip install alembic
export DATABASE_URL=sqlite:///./ecommerce.db  # or your Postgres URL
alembic upgrade head
```

## Docker
```bash
docker build -t api-ecommerce:local .
docker run -e DATABASE_URL=sqlite:///./ecommerce.db -e SECRET_KEY=devkey -p 8080:8080 api-ecommerce:local
```

## Google Cloud Run Deployment
- See `README_DEPLOY.md` for full step-by-step.
- Key steps:
  1. Build & push Docker image (Cloud Build or locally)
  2. Run Alembic migrations on Cloud SQL
  3. Deploy to Cloud Run with env vars and Cloud SQL connection

## CI/CD
- `cloudbuild.yaml` for Google Cloud Build
- `.github/workflows/deploy.yml` for GitHub Actions
- Both automate build, migration, and deploy


## Security & Production Notes
- Use Cloud SQL (Postgres) in production, not SQLite
- Store secrets in Secret Manager or GitHub Actions secrets
- Use a dedicated service account for Cloud Run with minimum permissions
- Add monitoring, logging, and custom domain as needed

## License
MIT

