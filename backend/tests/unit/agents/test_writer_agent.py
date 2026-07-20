import pytest
from backend.agents.writer_agent import WriterAgent
from backend.agents.base import AgentContext, Settings
from backend.agents.llm_provider import MockLLMProvider

@pytest.mark.asyncio
async def test_writer_agent():
    llm = MockLLMProvider(mock_content="Mock")
    agent = WriterAgent(llm, Settings())
    context = AgentContext(request_id="1", user_id="u1", platform="twitter")
    plan = {"topic": "Test"}
    
    result = await agent.run(context, plan)
    
    assert result.success is True
    variations = result.data["variations"]
    assert len(variations) >= 3
    for v in variations:
        assert "content" in v
        assert "hook" in v
        assert len(v["content"]) <= 280  # twitter limit logic is roughly mocked
