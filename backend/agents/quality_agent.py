import time

from pydantic import BaseModel, Field, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response


class QualityScoreResult(BaseModel):
    originality: float = Field(ge=0.0, le=1.0)
    hook_strength: float = Field(ge=0.0, le=1.0)
    engagement_predicted: float = Field(ge=0.0, le=1.0)
    spam_probability: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
    brand_consistency: float = Field(ge=0.0, le=1.0)
    human_score: float = Field(ge=0.0, le=1.0)
    grammar_issues: list[str] = Field(default_factory=list)
    duplicate_similarity: float = 0.0
    passed: bool = False
    rejection_reason: str | None = None


class QualityAgent(BaseAgent):
    name = "quality"
    description = "Scores content quality. Fails closed on unparseable output."

    def apply_thresholds(self, result: QualityScoreResult) -> QualityScoreResult:
        """Enforce configured minimums regardless of the LLM's own verdict."""
        s = self.settings
        failures = []
        if result.engagement_predicted < s.MIN_ENGAGEMENT_SCORE:
            failures.append(
                f"engagement {result.engagement_predicted:.2f} < {s.MIN_ENGAGEMENT_SCORE}"
            )
        if result.spam_probability > s.MAX_SPAM_SCORE:
            failures.append(f"spam {result.spam_probability:.2f} > {s.MAX_SPAM_SCORE}")
        if result.readability_score < s.MIN_READABILITY_SCORE:
            failures.append(
                f"readability {result.readability_score:.2f} < {s.MIN_READABILITY_SCORE}"
            )
        if result.brand_consistency < s.MIN_BRAND_CONSISTENCY:
            failures.append(
                f"brand consistency {result.brand_consistency:.2f} < {s.MIN_BRAND_CONSISTENCY}"
            )
        if result.human_score < s.MIN_HUMAN_SCORE:
            failures.append(f"human score {result.human_score:.2f} < {s.MIN_HUMAN_SCORE}")
        if result.duplicate_similarity >= s.MEMORY_SIMILARITY_THRESHOLD:
            failures.append(
                f"too similar to previous content ({result.duplicate_similarity:.2f})"
            )
        if failures:
            result.passed = False
            result.rejection_reason = "; ".join(failures)
        else:
            result.passed = True
            result.rejection_reason = None
        return result

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        content: str = kwargs["content"]
        duplicate_similarity: float = kwargs.get("duplicate_similarity", 0.0)
        start = time.monotonic()

        thresholds = {
            "min_engagement": self.settings.MIN_ENGAGEMENT_SCORE,
            "max_spam": self.settings.MAX_SPAM_SCORE,
            "min_readability": self.settings.MIN_READABILITY_SCORE,
            "min_brand_consistency": self.settings.MIN_BRAND_CONSISTENCY,
            "min_human_score": self.settings.MIN_HUMAN_SCORE,
        }
        prompt = self._build_prompt(
            content=content, platform=context.platform, thresholds=str(thresholds)
        )
        response = await self._call_llm(prompt, model=self.model, temperature=0.2)

        try:
            result = QualityScoreResult.model_validate(parse_json_response(response.content))
        except (AgentParseError, ValidationError) as exc:
            # Fail CLOSED: unparseable quality output rejects the draft.
            result = QualityScoreResult(
                originality=0.0,
                hook_strength=0.0,
                engagement_predicted=0.0,
                spam_probability=1.0,
                readability_score=0.0,
                brand_consistency=0.0,
                human_score=0.0,
                passed=False,
                rejection_reason=f"Quality evaluation unparseable: {exc}",
            )
            return AgentResult(
                success=True,
                data=result.model_dump(),
                tokens_used=response.tokens_used,
                duration_ms=self._elapsed_ms(start),
            )

        result.duplicate_similarity = max(result.duplicate_similarity, duplicate_similarity)
        result = self.apply_thresholds(result)

        return AgentResult(
            success=True,
            data=result.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
