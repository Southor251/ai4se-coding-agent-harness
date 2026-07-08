from agent_harness.models import AgentAction, TraceRecord
from agent_harness.models import Feedback
from agent_harness.trace.store import TraceStore
from agent_harness.web.theater import load_trace_for_display, summarize_trace


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
            "tool": "",
            "permission": "allow",
            "hitl": "",
            "tool_success": "",
            "tool_output": "",
            "tool_error": "",
            "feedback": "",
            "answer": "",
        }
    ]


def test_load_trace_for_display_includes_tool_details(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    store = TraceStore(trace_path)
    store.record(
        TraceRecord(
            step=1,
            llm_text='{"type":"call_tool"}',
            llm_action=AgentAction(
                type="call_tool",
                tool="read_file",
                args={"path": "README.md"},
            ),
            permission_verdict="allow",
            tool_result={"success": True, "output": "hello", "error": None},
            hitl_status=None,
        )
    )

    rows = load_trace_for_display(trace_path)

    assert rows[0]["tool"] == "read_file"
    assert rows[0]["tool_success"] is True
    assert rows[0]["tool_output"] == "hello"


def test_summarize_trace_counts_key_events():
    records = [
        {
            "step": 1,
            "llm_action": {"type": "call_tool", "tool": "read_file"},
            "permission_verdict": "allow",
            "feedback": {"category": "success"},
        },
        {
            "step": 2,
            "llm_action": {"type": "call_tool", "tool": "write_file"},
            "permission_verdict": "deny",
            "feedback": None,
        },
        {
            "step": 3,
            "llm_action": {"type": "done"},
            "permission_verdict": "allow",
            "feedback": None,
        },
    ]

    summary = summarize_trace(records)

    assert summary == {
        "steps": 3,
        "tool_calls": 2,
        "denials": 1,
        "feedback_events": 1,
    }


def test_summarize_trace_accepts_dataclass_records():
    records = [
        TraceRecord(
            step=1,
            llm_text="tool",
            llm_action=AgentAction(type="call_tool", tool="read_file"),
            permission_verdict="allow",
            feedback=Feedback(category="success", message="ok", raw="ok"),
        )
    ]

    summary = summarize_trace(records)

    assert summary["steps"] == 1
    assert summary["tool_calls"] == 1
    assert summary["feedback_events"] == 1
