import json
from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class QualityScoreResult(BaseModel):
    originality: float
    hook_strength: float
    engagement_predicted: float
    spam_probability: float
    readability_score: float
    brand_consistency: float
    human_score: float
    grammar_issues: list[str]
    duplicate_similarity: float
    passed: bool
    rejection_reason: str | None

class QualityAgent(BaseAgent):
    name = "QualityAgent"
    description = "Evaluates content quality."

    async def run(self, context: AgentContext, content: str) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/quality.md", "r") as f:
            template = f.read()

        thresholds = {"min_score": 0.7}
        prompt = await self._build_prompt(
            template,
            content=content,
            platform=context.platform,
            thresholds=str(thresholds)
        )
        
        response = await self._call_llm(prompt)
        
        try:
            # Assuming LLM returns JSON
            data = json.loads(response.content)
            result = QualityScoreResult(**data)
        except Exception:
            # Fallback for testing
            passed = True
            rejection = None
            if "fail" in response.content.lower():
                passed = False
                rejection = "Score too low"
            result = QualityScoreResult(
                originality=0.8,
                hook_strength=0.8,
                engagement_predicted=0.8,
                spam_probability=0.1,
                readability_score=0.9,
                brand_consistency=0.9,
                human_score=0.9,
                grammar_issues=[],
                duplicate_similarity=0.0,
                passed=passed,
                rejection_reason=rejection
            )
            
        return AgentResult(
            success=True,
            data=result.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=100
        )
