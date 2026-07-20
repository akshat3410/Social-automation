from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.error_handler import (
    global_exception_handler,
    social_engine_exception_handler,
)
from api.middleware.request_id import RequestIDMiddleware
from api.v1.router import api_router
from config.logging_config import configure_logging
from config.settings import get_settings
from database.session import init_db
from services.exceptions import SocialEngineError

settings = get_settings()
configure_logging(debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        await init_db()
    yield


app = FastAPI(
    title="Social Engine API",
    description="Self-hosted AI social media automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SocialEngineError, social_engine_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
