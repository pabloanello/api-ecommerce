# Deployment & Migrations: Google Cloud Run + Alembic

## 1. Build & Run Locally (Docker)

```bash
docker build -t api-ecommerce:local .
docker run -e DATABASE_URL=sqlite:///./ecommerce.db -e SECRET_KEY=devkey -p 8080:8080 api-ecommerce:local
```

## 2. Run Alembic Migrations

Install Alembic if needed:
```bash
pip install alembic
```

Set your database URL (SQLite or Postgres):
```bash
export DATABASE_URL=sqlite:///./ecommerce.db  # or your Postgres URL
alembic upgrade head
```

## 3. Deploy to Google Cloud Run

- Build & push image:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/api-ecommerce:latest
```
- Deploy to Cloud Run:
```bash
gcloud run deploy api-ecommerce \
  --image gcr.io/PROJECT_ID/api-ecommerce:latest \
  --region us-central1 \
  --platform managed \
  --add-cloudsql-instances PROJECT:REGION:INSTANCE \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql+psycopg2://DBUSER:DBPASS@/DBNAME?host=/cloudsql/PROJECT:REGION:INSTANCE",SECRET_KEY="..."
```

## 4. Run Alembic Migrations on Cloud SQL

Set `DATABASE_URL` to your Cloud SQL Postgres connection string and run:
```bash
alembic upgrade head
```

## 5. (Optional) GitHub Actions/Cloud Build
- Add a workflow step to run Alembic migrations after deploy.

---

- `alembic.ini` and `alembic/` are set up for migrations.
- `app/db.py` and `app/auth.py` use environment variables for config.
- For production, use Cloud SQL (Postgres) and set strong secrets.
