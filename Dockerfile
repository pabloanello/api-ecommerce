# Dockerfile for FastAPI app on Google Cloud Run
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install system dependencies for psycopg2 and bcrypt
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

# Use gunicorn with uvicorn worker for production
CMD exec gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:${PORT} app.main:app
