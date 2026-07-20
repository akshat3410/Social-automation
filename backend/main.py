from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import api_router
from api.middleware.request_id import RequestIDMiddleware
from api.middleware.error_handler import global_exception_handler, social_engine_exception_handler
from services.exceptions import SocialEngineError
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    yield

app = FastAPI(
    title="Social Engine API",
    description="Production-grade AI social media automation platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SocialEngineError, social_engine_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
