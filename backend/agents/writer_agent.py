import time

from pydantic import BaseModel, Field, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response

PLATFORM_CHAR_LIMITS = {"twitter": 280, "reddit": 40000}


class DraftVariation(BaseModel):
    content: str
    hook: str
    tone: str = "casual"
    hashtags: list[str] = Field(default_factory=list)


class WriterAgent(BaseAgent):
    name = "writer"
    description = "Generates content variations based on the plan."

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        plan: dict = kwargs["plan"]
        num_variations: int = kwargs.get("num_variations", 3)
        brand_examples: str = kwargs.get("brand_examples", "N/A")
        avoid_phrases: str = kwargs.get("avoid_phrases", "N/A")
        start = time.monotonic()

        limit = PLATFORM_CHAR_LIMITS.get(context.platform, 0)
        prompt = self._build_prompt(
            content_plan=str(plan),
            platform_limits=limit or "none",
            brand_examples=brand_examples,
            avoid_phrases=avoid_phrases,
            num_variations=num_variations,
        )
        response = await self._call_llm(prompt, model=self.model)

        try:
            raw = parse_json_response(response.content)
            if not isinstance(raw, list):
                raise AgentParseError("Expected a JSON list of variations")
            variations = [DraftVariation.model_validate(item) for item in raw]
        except (AgentParseError, ValidationError) as exc:
            return AgentResult(
                success=False,
                data={},
                error=f"Writer output parsing failed: {exc}",
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        if limit:
            variations = [v for v in variations if len(v.content) <= limit]
        if not variations:
            return AgentResult(
                success=False,
                data={},
                error="No variations satisfied the platform character limit",
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        return AgentResult(
            success=True,
            data={"variations": [v.model_dump() for v in variations]},
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
