from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from services.exceptions import (
    SocialEngineError,
    NotFoundError,
    UnauthorizedError,
    DuplicateContentError,
    QualityGateFailedError,
    ProviderError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

async def social_engine_exception_handler(request: Request, exc: SocialEngineError):
    status_code = 400
    if isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, UnauthorizedError):
        status_code = 401
    elif isinstance(exc, DuplicateContentError):
        status_code = 409
    elif isinstance(exc, RateLimitError):
        status_code = 429
    
    return JSONResponse(
        status_code=status_code,
        content={"error": exc.__class__.__name__, "message": str(exc)}
    )

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception [req_id={request_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "An unexpected error occurred."}
    )
