from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only auto-create tables for SQLite (dev). PostgreSQL uses Alembic migrations.
    if "sqlite" in settings.database_url.lower():
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sefaria LaTeX API",
    version="1.0.0",
    description="Generate printable PDFs from Sefaria texts",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
