import time

from pydantic import BaseModel, Field, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response


class ResearchOutput(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    trending_topics: list[str] = Field(default_factory=list)
    suggested_angles: list[str] = Field(default_factory=list)


class ResearchAgent(BaseAgent):
    name = "research"
    description = "Synthesizes raw research material into insights and angles."

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        topic: str = kwargs["topic"]
        trending_context: str = kwargs.get("trending_context", "N/A")
        previous_posts_summary: str = kwargs.get("previous_posts_summary", "N/A")
        start = time.monotonic()

        prompt = self._build_prompt(
            topic=topic,
            platform=context.platform,
            previous_posts_summary=previous_posts_summary,
            trending_context=trending_context,
        )
        response = await self._call_llm(prompt, model=self.model)

        try:
            data = ResearchOutput.model_validate(parse_json_response(response.content))
        except (AgentParseError, ValidationError) as exc:
            return AgentResult(
                success=False,
                data={},
                error=f"Research output parsing failed: {exc}",
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        return AgentResult(
            success=True,
            data=data.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
