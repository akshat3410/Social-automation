import json

from agents.base import AgentContext
from agents.llm_provider import MockLLMProvider
from agents.quality_agent import QualityAgent
from config.settings import get_settings

QUALITY_TEMPLATE = "Score: {content} on {platform} with {thresholds}"


def make_agent(mock_content: str) -> QualityAgent:
    return QualityAgent(
        MockLLMProvider(mock_content=mock_content),
        get_settings(),
        QUALITY_TEMPLATE,
        model="test-model",
    )


def make_context() -> AgentContext:
    return AgentContext(request_id="1", user_id="u1", platform="twitter")


GOOD_SCORES = {
    "originality": 0.9,
    "hook_strength": 0.8,
    "engagement_predicted": 0.8,
    "spam_probability": 0.1,
    "readability_score": 0.9,
    "brand_consistency": 0.9,
    "human_score": 0.9,
    "grammar_issues": [],
    "duplicate_similarity": 0.0,
    "passed": True,
    "rejection_reason": None,
}


async def test_quality_agent_passes_good_content():
    agent = make_agent(json.dumps(GOOD_SCORES))
    result = await agent.run(make_context(), content="Test content")

    assert result.success is True
    assert result.data["passed"] is True
    assert result.data["rejection_reason"] is None
    assert result.data["originality"] == 0.9


async def test_quality_agent_thresholds_override_llm_verdict():
    # The LLM claims "passed", but the scores are below configured thresholds:
    # the gate must reject anyway.
    scores = dict(GOOD_SCORES, engagement_predicted=0.1, passed=True)
    agent = make_agent(json.dumps(scores))
    result = await agent.run(make_context(), content="Weak content")

    assert result.success is True
    assert result.data["passed"] is False
    assert "engagement" in result.data["rejection_reason"]


async def test_quality_agent_fails_closed_on_malformed_output():
    agent = make_agent("Sure! Here's my assessment: it looks great!")
    result = await agent.run(make_context(), content="Anything")

    assert result.success is True
    assert result.data["passed"] is False
    assert "unparseable" in result.data["rejection_reason"].lower()


async def test_quality_agent_rejects_duplicates():
    agent = make_agent(json.dumps(GOOD_SCORES))
    result = await agent.run(make_context(), content="Same again", duplicate_similarity=0.95)

    assert result.data["passed"] is False
    assert "similar" in result.data["rejection_reason"]


async def test_quality_agent_parses_fenced_json():
    agent = make_agent(f"```json\n{json.dumps(GOOD_SCORES)}\n```")
    result = await agent.run(make_context(), content="Fenced")

    assert result.data["passed"] is True
