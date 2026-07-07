# Task 1.4: OpenAILLM

**Files:**
- Create: `src/agent_harness/llm/openai.py`
- Update: `tests/test_llm.py`

**Goal:** Real OpenAI API implementation of LLMInterface.

**Dependencies:** T1.2 (LLMInterface)

## Implementation

```python
# src/agent_harness/llm/openai.py
import os
from openai import OpenAI
from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.models import AgentAction

class OpenAILLM(LLMInterface):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(text="API key not configured", action=AgentAction(type="done"))
        # Build messages from context
        messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in context]
        # Add tool definitions as system content
        if menu:
            tool_desc = "\n".join([f"- {t.get('name', '?')}: {t.get('description', '')}" for t in menu])
            messages.append({"role": "system", "content": f"Available tools:\n{tool_desc}"})
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            text = response.choices[0].message.content or ""
            # Simple parse: look for "action: <type>" at end of text
            action = AgentAction(type="done")
            if "action: call_tool" in text.lower():
                action = AgentAction(type="call_tool")
            return LLMResponse(text=text, action=action)
        except Exception as e:
            return LLMResponse(text=f"API error: {e}", action=AgentAction(type="done"))
```

## Tests

```python
# tests/test_llm.py (add)
def test_openai_llm_no_key():
    llm = OpenAILLM(api_key="")
    result = llm.call([], [])
    assert result.action.type == "done"
    assert "not configured" in result.text
```