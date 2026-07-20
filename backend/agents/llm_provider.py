from abc import ABC, abstractmethod
from typing import Literal

import httpx
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .base import LLMResponse


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or code >= 500
    return isinstance(exc, (httpx.TransportError, httpx.TimeoutException))


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self, messages: list[Message], model: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def embed(self, text: str, model: str) -> list[float]:
        ...

    async def aclose(self) -> None:  # noqa: B027 - optional hook
        pass


class OpenRouterProvider(LLMProvider):
    """OpenAI-compatible chat provider (OpenRouter by default)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float = 60.0,
        embeddings_api_key: str | None = None,
        embeddings_base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.embeddings_api_key = embeddings_api_key
        self.embeddings_base_url = embeddings_base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    async def complete(
        self, messages: list[Message], model: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = await self._client.post(
            f"{self.base_url}/chat/completions", json=payload, headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", model),
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            finish_reason=data["choices"][0].get("finish_reason"),
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    async def embed(self, text: str, model: str) -> list[float]:
        if not self.embeddings_api_key:
            raise NotImplementedError(
                "Embeddings are not configured; set EMBEDDINGS_API_KEY to enable memory features"
            )
        headers = {"Authorization": f"Bearer {self.embeddings_api_key}"}
        response = await self._client.post(
            f"{self.embeddings_base_url}/embeddings",
            json={"model": model, "input": text},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    async def aclose(self) -> None:
        await self._client.aclose()


class MockLLMProvider(LLMProvider):
    """Test double. Returns pre-configured content and records calls."""

    def __init__(self, mock_content: str = "Mock response"):
        self.mock_content = mock_content
        self.calls: list[dict] = []

    async def complete(
        self, messages: list[Message], model: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        self.calls.append({"messages": messages, "model": model})
        return LLMResponse(
            content=self.mock_content, model=model, tokens_used=42, finish_reason="stop"
        )

    async def embed(self, text: str, model: str) -> list[float]:
        self.calls.append({"text": text, "model": model})
        return [0.0] * 1536


def build_llm_provider(settings) -> OpenRouterProvider:
    """Construct the configured LLM provider from settings."""
    return OpenRouterProvider(
        api_key=settings.AI_API_KEY,
        base_url=settings.AI_BASE_URL,
        timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
        embeddings_api_key=settings.EMBEDDINGS_API_KEY,
        embeddings_base_url=settings.EMBEDDINGS_BASE_URL,
    )
