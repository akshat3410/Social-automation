from pydantic import BaseModel
from .base import BaseAgent, AgentContext, AgentResult

class EditorAgent(BaseAgent):
    name = "EditorAgent"
    description = "Edits and refines content."

    async def run(self, context: AgentContext, draft: dict) -> AgentResult:
        with open("/Users/akshatsoni/teamwork_projects/social_engine/backend/prompts/editor.md", "r") as f:
            template = f.read()

        prompt = await self._build_prompt(
            template,
            draft_content=draft.get("content", ""),
            platform=context.platform,
            brand_guidelines="N/A"
        )
        
        response = await self._call_llm(prompt)
        
        edited_content = "Edited content"
        changelog = ["Fixed grammar", "Removed AI phrases"]
        
        return AgentResult(
            success=True,
            data={"content": edited_content, "changelog": changelog},
            tokens_used=response.tokens_used,
            duration_ms=100
        )
