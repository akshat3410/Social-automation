from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    finish_reason: str | None = None

class AgentContext(BaseModel):
    request_id: str
    user_id: str
    platform: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class AgentResult(BaseModel):
    success: bool
    data: dict[str, Any]
    error: str | None = None
    tokens_used: int = 0
    duration_ms: int = 0

class Settings(BaseModel):
    # Dummy settings class to type hint
    pass

class BaseAgent(ABC):
    name: str
    description: str

    def __init__(self, llm_provider, settings: Settings):
        self.llm_provider = llm_provider
        self.settings = settings

    @abstractmethod
    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        pass

    async def _build_prompt(self, template: str, **kwargs) -> str:
        # Very simple templating for now
        return template.format(**kwargs)

    async def _call_llm(self, prompt: str, **kwargs) -> LLMResponse:
        from .llm_provider import Message
        messages = [Message(role="user", content=prompt)]
        # For simplicity, default args
        model = kwargs.get("model", "default-model")
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        return await self.llm_provider.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
