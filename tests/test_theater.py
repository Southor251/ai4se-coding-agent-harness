from agent_harness.models import AgentAction, TraceRecord
from agent_harness.trace.store import TraceStore
from agent_harness.web.theater import load_trace_for_display


def test_load_trace_for_display(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    store = TraceStore(trace_path)
    store.record(
        TraceRecord(
            step=1,
            llm_text="done",
            llm_action=AgentAction(type="done"),
            permission_verdict="allow",
        )
    )

    rows = load_trace_for_display(trace_path)

    assert rows == [
        {
            "step": 1,
            "llm": "done",
            "action": "done",
            "permission": "allow",
            "feedback": "",
        }
    ]
