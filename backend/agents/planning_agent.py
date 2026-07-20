from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class ContentPlan(BaseModel):
    topic: str
    target_audience: str
    platform: str
    tone: str
    goal: str
    key_message: str
    content_type: str
    estimated_performance: str

class PlanningAgent(BaseAgent):
    name = "PlanningAgent"
    description = "Plans content based on research."

    async def run(self, context: AgentContext, research_data: dict) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/planning.md", "r") as f:
            template = f.read()

        prompt = await self._build_prompt(
            template,
            research_summary=research_data.get("summary", ""),
            user_goals="Engagement",
            brand_voice="Professional"
        )
        
        response = await self._call_llm(prompt)
        
        plan = ContentPlan(
            topic="Tech",
            target_audience="Devs",
            platform=context.platform,
            tone="Informative",
            goal="awareness",
            key_message="Learn tech",
            content_type="post",
            estimated_performance="High"
        ).model_dump()
        
        return AgentResult(
            success=True,
            data=plan,
            tokens_used=response.tokens_used,
            duration_ms=100
        )
