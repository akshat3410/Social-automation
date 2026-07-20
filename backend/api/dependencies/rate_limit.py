"""Lightweight Redis fixed-window rate limiting.

Fails open when Redis is unreachable so the API still works in
environments without Redis (unit tests, degraded infrastructure).
"""
import logging
from collections.abc import Awaitable, Callable

import redis.asyncio as aioredis
from fastapi import Request

from config.settings import get_settings
from services.exceptions import RateLimitError

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            get_settings().REDIS_URL, socket_connect_timeout=1, socket_timeout=1
        )
    return _redis_client


def rate_limit(scope: str, limit_per_minute: int) -> Callable[[Request], Awaitable[None]]:
    async def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{scope}:{client_ip}"
        try:
            client = _get_redis()
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, 60)
            if count > limit_per_minute:
                raise RateLimitError(f"Rate limit exceeded for {scope}; retry in a minute")
        except RateLimitError:
            raise
        except Exception as exc:  # Redis down: fail open, but say so.
            logger.warning("Rate limiter unavailable (%s); allowing request", exc)

    return _dependency


def auth_rate_limit() -> Callable[[Request], Awaitable[None]]:
    return rate_limit("auth", get_settings().RATE_LIMIT_AUTH_PER_MINUTE)


def generate_rate_limit() -> Callable[[Request], Awaitable[None]]:
    return rate_limit("generate", get_settings().RATE_LIMIT_GENERATE_PER_MINUTE)
