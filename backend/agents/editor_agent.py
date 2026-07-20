import time

from pydantic import BaseModel, Field, ValidationError

from .base import AgentContext, AgentParseError, AgentResult, BaseAgent, parse_json_response


class EditedDraft(BaseModel):
    content: str
    changelog: list[str] = Field(default_factory=list)


class EditorAgent(BaseAgent):
    name = "editor"
    description = "Edits and refines content, removing AI-isms."

    async def run(self, context: AgentContext, **kwargs) -> AgentResult:
        draft_content: str = kwargs["draft_content"]
        brand_guidelines: str = kwargs.get("brand_guidelines", "N/A")
        start = time.monotonic()

        prompt = self._build_prompt(
            draft_content=draft_content,
            platform=context.platform,
            brand_guidelines=brand_guidelines,
        )
        response = await self._call_llm(prompt, model=self.model)

        try:
            edited = EditedDraft.model_validate(parse_json_response(response.content))
        except (AgentParseError, ValidationError):
            # Editing is a refinement step: if the editor response is
            # unparseable, keep the original draft rather than failing
            # the whole pipeline.
            edited = EditedDraft(content=draft_content, changelog=["Editing skipped: unparseable editor output"])

        return AgentResult(
            success=True,
            data=edited.model_dump(),
            tokens_used=response.tokens_used,
            duration_ms=self._elapsed_ms(start),
        )
