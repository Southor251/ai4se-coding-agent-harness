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