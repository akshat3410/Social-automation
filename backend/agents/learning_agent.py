from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class LearningResult(BaseModel):
    insights: list[str]
    memory_updates_count: int

class LearningAgent(BaseAgent):
    name = "LearningAgent"
    description = "Learns from analytics and updates memory."

    def __init__(self, llm_provider, settings, memory_service):
        super().__init__(llm_provider, settings)
        self.memory_service = memory_service

    async def run(self, context: AgentContext, post_content: str, analytics: dict) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/learning.md", "r") as f:
            template = f.read()

        prompt = await self._build_prompt(
            template,
            post_content=post_content,
            analytics_data=str(analytics),
            previous_performance="N/A"
        )
        
        response = await self._call_llm(prompt)
        
        # Parse insights
        insights = ["Insight 1"]
        
        # Update memory via service
        await self.memory_service.store(
            content=f"Post insights: {insights}",
            type="insight",
            user_id=context.user_id,
            metadata={"platform": context.platform}
        )
        
        result = LearningResult(
            insights=insights,
            memory_updates_count=1
        )
        
        return AgentResult(
            success=True,
            data=result.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=100
        )
