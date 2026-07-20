import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from config.settings import Settings


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


class AgentParseError(Exception):
    """Raised when an LLM response cannot be parsed into the expected shape."""


def parse_json_response(text: str) -> Any:
    """Parse JSON out of an LLM response, tolerating markdown code fences."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    # Fall back to the first {...} or [...] block in the text.
    if not cleaned.startswith(("{", "[")):
        match = re.search(r"[\[{].*[\]}]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AgentParseError(f"LLM returned invalid JSON: {exc}") from exc


class BaseAgent(ABC):
    """Base class for all agents.

    Agents receive their prompt template (from PromptService or a file) and an
    LLM provider; they never touch the database or the filesystem.
    """

    name: str
    description: str

    def __init__(
        self,
        llm_provider: Any,
        settings: Settings,
        prompt_template: str,
        model: str | None = None,
    ):
        self.llm_provider = llm_provider
        self.settings = settings
        self.prompt_template = prompt_template
        self.model = model

    @abstractmethod
    async def run(self, context: AgentContext, **kwargs: Any) -> AgentResult:
        ...

    def _build_prompt(self, **kwargs: Any) -> str:
        return self.prompt_template.format(**kwargs)

    async def _call_llm(self, prompt: str, **kwargs: Any) -> LLMResponse:
        from .llm_provider import Message

        messages = [Message(role="user", content=prompt)]
        return await self.llm_provider.complete(
            messages=messages,
            model=kwargs.get("model", self.model or self.settings.MODEL_WRITING),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

    @staticmethod
    def _elapsed_ms(start: float) -> int:
        return int((time.monotonic() - start) * 1000)
