import pytest
import json
from backend.agents.quality_agent import QualityAgent
from backend.agents.base import AgentContext, Settings
from backend.agents.llm_provider import MockLLMProvider

@pytest.mark.asyncio
async def test_quality_agent_success():
    mock_response = {
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
        "rejection_reason": None
    }
    llm = MockLLMProvider(mock_content=json.dumps(mock_response))
    agent = QualityAgent(llm, Settings())
    context = AgentContext(request_id="1", user_id="u1", platform="twitter")
    
    result = await agent.run(context, "Test content")
    
    assert result.success is True
    assert result.data["passed"] is True
    assert result.data["rejection_reason"] is None
    assert result.data["originality"] == 0.9

@pytest.mark.asyncio
async def test_quality_agent_fail():
    mock_response = {
        "originality": 0.4,
        "hook_strength": 0.4,
        "engagement_predicted": 0.4,
        "spam_probability": 0.8,
        "readability_score": 0.4,
        "brand_consistency": 0.4,
        "human_score": 0.4,
        "grammar_issues": ["Bad grammar"],
        "duplicate_similarity": 0.9,
        "passed": False,
        "rejection_reason": "Score too low"
    }
    llm = MockLLMProvider(mock_content=json.dumps(mock_response))
    agent = QualityAgent(llm, Settings())
    context = AgentContext(request_id="1", user_id="u1", platform="twitter")
    
    result = await agent.run(context, "Fail content")
    
    assert result.success is True
    assert result.data["passed"] is False
    assert result.data["rejection_reason"] == "Score too low"
