from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router
from .db.base import Base
from .db.session import engine

# Create DB tables (sqlite, simple)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
