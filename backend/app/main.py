from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.core import settings
from app.services.monitoring import get_runtime_status

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.get("/status")
def status() -> dict:
    return {
        "status": "ok",
        **get_runtime_status(),
    }


app.include_router(v1_router, prefix=settings.api_prefix)
