import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ECDAT API",
    description="Cryptographic Discovery & Quantum Readiness Platform",
    version="1.0.0",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("ECDAT API started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ECDAT API shutdown")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}