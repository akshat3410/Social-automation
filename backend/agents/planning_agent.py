import time

from pydantic import BaseModel, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response


class ContentPlan(BaseModel):
    topic: str
    target_audience: str
    platform: str
    tone: str
    goal: str
    key_message: str
    content_type: str = "post"


class PlanningAgent(BaseAgent):
    name = "planning"
    description = "Plans content based on research."

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        research_data: dict = kwargs["research_data"]
        user_goals: str = kwargs.get("user_goals", "engagement")
        brand_voice: str = kwargs.get("brand_voice", "authentic, knowledgeable")
        start = time.monotonic()

        prompt = self._build_prompt(
            research_summary=research_data.get("summary", ""),
            user_goals=user_goals,
            brand_voice=brand_voice,
        )
        response = await self._call_llm(prompt, model=self.model)

        try:
            plan = ContentPlan.model_validate(parse_json_response(response.content))
        except (AgentParseError, ValidationError) as exc:
            return AgentResult(
                success=False,
                data={},
                error=f"Plan output parsing failed: {exc}",
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        return AgentResult(
            success=True,
            data=plan.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
