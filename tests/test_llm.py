import pytest
from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction


from agent_harness.llm.openai import OpenAILLM


def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        LLMInterface()


def test_mock_llm_returns_preset():
    expected = LLMResponse(text="hello", action=AgentAction(type="done"))
    mock = MockLLM(responses=[expected])
    result = mock.call([], [])
    assert result.text == "hello"
    assert result.action.type == "done"


def test_mock_llm_consumes_queue():
    r1 = LLMResponse(text="first", action=AgentAction(type="call_tool", tool="read_file"))
    r2 = LLMResponse(text="second", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    assert mock.call([], []).text == "first"
    assert mock.call([], []).text == "second"


def test_mock_llm_call_tool_when_exhausted():
    mock = MockLLM(responses=[])
    result = mock.call([], [])
    assert result.action.type == "call_tool"


def test_openai_llm_no_key():
    llm = OpenAILLM(api_key="")
    result = llm.call([], [])
    assert result.action.type == "done"
    assert "not configured" in result.text


class FakeOpenAIMessage:
    content = 'action: call_tool\ntool: read_file\nargs: {"path": "README.md"}'


class FakeOpenAIChoice:
    message = FakeOpenAIMessage()


class FakeOpenAIResponse:
    choices = [FakeOpenAIChoice()]


class FakeCompletions:
    def create(self, **kwargs):
        return FakeOpenAIResponse()


class FakeChat:
    completions = FakeCompletions()


class FakeClient:
    chat = FakeChat()


def test_openai_llm_parses_text_tool_action():
    llm = OpenAILLM(api_key="test-key")
    llm._client = FakeClient()

    result = llm.call([], [{"name": "read_file", "description": "read"}])

    assert result.action.type == "call_tool"
    assert result.action.tool == "read_file"
    assert result.action.args == {"path": "README.md"}
