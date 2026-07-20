"""Regression tests for prompt templates.

Guards against two audit findings: prompts loaded from hardcoded absolute
paths, and templates drifting from the variables agents actually pass.
"""
from typing import Any

from config.settings import get_settings
from models.prompt_version import AgentNameEnum

EXPECTED_VARIABLES: dict[str, dict[str, Any]] = {
    "research": {
        "topic": "t",
        "platform": "twitter",
        "previous_posts_summary": "s",
        "trending_context": "c",
    },
    "planning": {"research_summary": "r", "user_goals": "g", "brand_voice": "v"},
    "writer": {
        "content_plan": "p",
        "platform_limits": 280,
        "brand_examples": "e",
        "avoid_phrases": "a",
        "num_variations": 3,
    },
    "editor": {"draft_content": "d", "platform": "twitter", "brand_guidelines": "g"},
    "quality": {"content": "c", "platform": "twitter", "thresholds": "t"},
    "learning": {
        "post_content": "p",
        "analytics_data": "a",
        "previous_performance": "pp",
    },
}


def test_prompt_file_exists_for_every_agent():
    prompts_dir = get_settings().PROMPTS_DIR
    assert prompts_dir.is_dir(), f"Prompts directory missing: {prompts_dir}"
    for agent in AgentNameEnum:
        path = prompts_dir / f"{agent.value}.md"
        assert path.is_file(), f"Missing prompt file for agent '{agent.value}'"


def test_prompt_templates_format_with_expected_variables():
    prompts_dir = get_settings().PROMPTS_DIR
    for agent_name, variables in EXPECTED_VARIABLES.items():
        template = (prompts_dir / f"{agent_name}.md").read_text()
        rendered = template.format(**variables)
        assert rendered, f"Template for '{agent_name}' rendered empty"


def test_prompts_dir_is_inside_the_repo():
    prompts_dir = get_settings().PROMPTS_DIR.resolve()
    backend_dir = prompts_dir.parent
    assert (backend_dir / "main.py").is_file(), (
        "PROMPTS_DIR must resolve relative to the backend package, "
        f"got {prompts_dir}"
    )
