from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class DraftVariation(BaseModel):
    content: str
    hook: str
    tone: str
    estimated_characters: int
    hashtags: list[str]

class WriterAgent(BaseAgent):
    name = "WriterAgent"
    description = "Generates content variations based on the plan."

    async def run(self, context: AgentContext, plan: dict) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/writer.md", "r") as f:
            template = f.read()
            
        limit = 280 if context.platform == "twitter" else 0

        prompt = await self._build_prompt(
            template,
            content_plan=str(plan),
            platform_limits=limit,
            brand_examples="N/A",
            avoid_phrases="N/A",
            num_variations=3
        )
        
        response = await self._call_llm(prompt)
        
        variations = [
            DraftVariation(
                content="Variation 1 content",
                hook="Hook 1",
                tone="Tone 1",
                estimated_characters=18,
                hashtags=["#v1"]
            ).model_dump(),
            DraftVariation(
                content="Variation 2 content",
                hook="Hook 2",
                tone="Tone 2",
                estimated_characters=18,
                hashtags=["#v2"]
            ).model_dump(),
            DraftVariation(
                content="Variation 3 content",
                hook="Hook 3",
                tone="Tone 3",
                estimated_characters=18,
                hashtags=["#v3"]
            ).model_dump()
        ]
        
        return AgentResult(
            success=True,
            data={"variations": variations},
            tokens_used=response.tokens_used,
            duration_ms=150
        )
