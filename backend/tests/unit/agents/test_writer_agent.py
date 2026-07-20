import json

from agents.base import AgentContext
from agents.llm_provider import MockLLMProvider
from agents.writer_agent import WriterAgent
from config.settings import get_settings

WRITER_TEMPLATE = (
    "Plan: {content_plan} Limits: {platform_limits} Examples: {brand_examples} "
    "Avoid: {avoid_phrases} N: {num_variations}"
)


def make_agent(mock_content: str) -> WriterAgent:
    return WriterAgent(
        MockLLMProvider(mock_content=mock_content),
        get_settings(),
        WRITER_TEMPLATE,
        model="test-model",
    )


def make_context(platform: str = "twitter") -> AgentContext:
    return AgentContext(request_id="1", user_id="u1", platform=platform)


VARIATIONS = [
    {"content": "Short tweet one", "hook": "Question", "tone": "casual", "hashtags": []},
    {"content": "Short tweet two", "hook": "Bold claim", "tone": "casual", "hashtags": ["#ai"]},
    {"content": "Short tweet three", "hook": "Statistic", "tone": "formal", "hashtags": []},
]


async def test_writer_agent_parses_variations():
    agent = make_agent(json.dumps(VARIATIONS))
    result = await agent.run(make_context(), plan={"topic": "Test"}, num_variations=3)

    assert result.success is True
    variations = result.data["variations"]
    assert len(variations) == 3
    for v in variations:
        assert v["content"]
        assert v["hook"]
        assert len(v["content"]) <= 280


async def test_writer_agent_filters_over_limit_variations():
    over_limit = dict(VARIATIONS[0], content="x" * 300)
    agent = make_agent(json.dumps([over_limit, VARIATIONS[1]]))
    result = await agent.run(make_context(), plan={"topic": "Test"})

    assert result.success is True
    assert len(result.data["variations"]) == 1


async def test_writer_agent_fails_on_malformed_output():
    agent = make_agent("Here are some tweet ideas for you!")
    result = await agent.run(make_context(), plan={"topic": "Test"})

    assert result.success is False
    assert result.error is not None


async def test_writer_agent_fails_when_all_variations_too_long():
    over = [dict(VARIATIONS[0], content="x" * 300)]
    agent = make_agent(json.dumps(over))
    result = await agent.run(make_context(), plan={"topic": "Test"})

    assert result.success is False
