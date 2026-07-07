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
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeOpenAIResponse()


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeClient:
    def __init__(self):
        self.chat = FakeChat()


def test_openai_llm_parses_text_tool_action():
    llm = OpenAILLM(api_key="test-key")
    client = FakeClient()
    llm._client = client

    result = llm.call([], [{"name": "read_file", "description": "read"}])

    assert result.action.type == "call_tool"
    assert result.action.tool == "read_file"
    assert result.action.args == {"path": "README.md"}


def test_openai_llm_passes_model_and_temperature_to_client():
    llm = OpenAILLM(api_key="test-key", model="custom-model", temperature=0.2)
    client = FakeClient()
    llm._client = client

    llm.call([{"role": "user", "content": "hello"}], [])

    assert client.chat.completions.last_kwargs["model"] == "custom-model"
    assert client.chat.completions.last_kwargs["temperature"] == 0.2
    assert client.chat.completions.last_kwargs["messages"] == [
        {"role": "user", "content": "hello"}
    ]


def test_openai_llm_builds_client_with_base_url():
    llm = OpenAILLM(api_key="test-key", model="custom-model", base_url="https://example.test/v1")

    assert llm.base_url == "https://example.test/v1"
