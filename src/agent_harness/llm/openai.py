import os
from openai import OpenAI
from agent_harness.llm.action_protocol import action_protocol_prompt, parse_agent_action
from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.models import AgentAction


class OpenAILLM(LLMInterface):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4",
        base_url: str | None = None,
        temperature: float = 0.7,
        client=None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self._client = client

    def _get_client(self) -> OpenAI:
        if self._client is None:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(text="API key not configured", action=AgentAction(type="done"))
        messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in context]
        if menu:
            tool_desc = "\n".join([f"- {t.get('name', '?')}: {t.get('description', '')}" for t in menu])
            messages.append({"role": "system", "content": f"Available tools:\n{tool_desc}"})
        messages.append({"role": "system", "content": action_protocol_prompt(menu)})
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            text = response.choices[0].message.content or ""
            action = parse_agent_action(text)
            return LLMResponse(text=text, action=action)
        except Exception as e:
            return LLMResponse(text=f"API error: {e}", action=AgentAction(type="done"))
