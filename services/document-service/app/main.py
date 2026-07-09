from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, health
from app.core.config import settings
from app.db.base import init_db
from app.services.storage import ensure_storage_dirs


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_dirs()
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Document Service for The QCM App: PDF upload, deletion, listing, extraction and cache.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "document-service", "status": "running"}
