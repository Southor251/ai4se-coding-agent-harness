from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction
from agent_harness.trace.store import TraceStore


def test_agent_loop_records_trace(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    mock = MockLLM(responses=[LLMResponse(text="done", action=AgentAction(type="done"))])
    harness = Harness(llm=mock, trace=TraceStore(trace_path), max_steps=5)

    agent_loop("test", harness)

    records = TraceStore.load(trace_path)
    assert records[0]["step"] == 1
    assert records[0]["llm_text"] == "done"
    assert records[0]["permission_verdict"] == "allow"
