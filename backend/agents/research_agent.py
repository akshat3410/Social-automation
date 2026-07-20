from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class ResearchResult(BaseModel):
    summary: str
    key_points: list[str]
    trending_topics: list[str]
    suggested_angles: list[str]
    raw_sources: list[str]

class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    description = "Gathers research data and synthesizes insights."

    async def run(self, context: AgentContext, topic: str) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/research.md", "r") as f:
            template = f.read()

        prompt = await self._build_prompt(
            template,
            topic=topic,
            platform=context.platform,
            previous_posts_summary="N/A",
            trending_context="N/A"
        )
        
        response = await self._call_llm(prompt)
        
        # In a real scenario, we'd parse response.content into ResearchResult
        # Mocking for now
        data = ResearchResult(
            summary=response.content[:50],
            key_points=["Point 1"],
            trending_topics=["Trend 1"],
            suggested_angles=["Angle 1"],
            raw_sources=["Source 1"]
        ).model_dump()
        
        return AgentResult(
            success=True,
            data=data,
            tokens_used=response.tokens_used,
            duration_ms=100
        )
