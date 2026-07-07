import os
import json
from openai import OpenAI
from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.models import AgentAction


class OpenAILLM(LLMInterface):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self._client = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(text="API key not configured", action=AgentAction(type="done"))
        messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in context]
        if menu:
            tool_desc = "\n".join([f"- {t.get('name', '?')}: {t.get('description', '')}" for t in menu])
            messages.append({"role": "system", "content": f"Available tools:\n{tool_desc}"})
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            text = response.choices[0].message.content or ""
            action = self._parse_text_action(text)
            return LLMResponse(text=text, action=action)
        except Exception as e:
            return LLMResponse(text=f"API error: {e}", action=AgentAction(type="done"))

    def _parse_text_action(self, text: str) -> AgentAction:
        fields = {}
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()

        if fields.get("action", "").lower() != "call_tool":
            return AgentAction(type="done")

        args = {}
        if fields.get("args"):
            try:
                parsed_args = json.loads(fields["args"])
                if isinstance(parsed_args, dict):
                    args = parsed_args
            except json.JSONDecodeError:
                args = {}
        return AgentAction(type="call_tool", tool=fields.get("tool"), args=args)
