import time

from pydantic import BaseModel, Field, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response


class LearningOutput(BaseModel):
    insights: list[str] = Field(default_factory=list)


class LearningAgent(BaseAgent):
    name = "learning"
    description = "Learns from analytics and updates brand memory."

    def __init__(self, llm_provider, settings, prompt_template, memory_service, model=None):
        super().__init__(llm_provider, settings, prompt_template, model)
        self.memory_service = memory_service

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        post_content: str = kwargs["post_content"]
        analytics: dict = kwargs["analytics"]
        previous_performance: str = kwargs.get("previous_performance", "N/A")
        start = time.monotonic()

        prompt = self._build_prompt(
            post_content=post_content,
            analytics_data=str(analytics),
            previous_performance=previous_performance,
        )
        response = await self._call_llm(prompt, model=self.model)

        try:
            output = LearningOutput.model_validate(parse_json_response(response.content))
        except (AgentParseError, ValidationError) as exc:
            return AgentResult(
                success=False,
                data={},
                error=f"Learning output parsing failed: {exc}",
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        stored = 0
        for insight in output.insights:
            saved = await self.memory_service.store(
                content=insight,
                type="style",
                user_id=context.user_id,
                metadata={"platform": context.platform, "source": "learning_agent"},
            )
            if saved is not None:
                stored += 1

        return AgentResult(
            success=True,
            data={"insights": output.insights, "memory_updates_count": stored},
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
