from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from .base import LLMResponse

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[Message], model: str, temperature: float, max_tokens: int) -> LLMResponse:
        pass

    @abstractmethod
    async def embed(self, text: str, model: str) -> list[float]:
        pass

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def complete(self, messages: list[Message], model: str, temperature: float, max_tokens: int) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": [m.model_dump() for m in messages],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                finish_reason=data["choices"][0].get("finish_reason")
            )
            
    async def embed(self, text: str, model: str) -> list[float]:
        # Dummy implementation for OpenRouter embed as it's not standard
        return [0.1] * 1536

class OpenAIProvider(OpenRouterProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key)
        self.base_url = base_url

class MockLLMProvider(LLMProvider):
    def __init__(self, mock_content: str = "Mock response"):
        self.mock_content = mock_content
        self.calls = []

    async def complete(self, messages: list[Message], model: str, temperature: float, max_tokens: int) -> LLMResponse:
        self.calls.append({"messages": messages, "model": model})
        return LLMResponse(
            content=self.mock_content,
            model=model,
            tokens_used=42,
            finish_reason="stop"
        )

    async def embed(self, text: str, model: str) -> list[float]:
        self.calls.append({"text": text, "model": model})
        return [0.0] * 1536
