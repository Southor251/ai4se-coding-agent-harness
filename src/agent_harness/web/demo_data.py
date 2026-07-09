from pathlib import Path

from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.store import HITLStore
from agent_harness.models import AgentAction, Feedback, ToolResult, TraceRecord
from agent_harness.trace.store import TraceStore


def ensure_demo_trace(trace_path: str, store_path: str) -> dict[str, str]:
    trace_file = Path(trace_path)
    store_file = Path(store_path)
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    store_file.parent.mkdir(parents=True, exist_ok=True)
    trace_file.write_text("", encoding="utf-8")

    store = TraceStore(trace_file)
    read_action = AgentAction(type="call_tool", tool="read_file", args={"path": "README.md"})
    write_action = AgentAction(
        type="call_tool",
        tool="write_file",
        args={"path": ".harness/demo-note.txt", "content": "judge demo approved"},
        changed_code=True,
    )
    done_action = AgentAction(type="done", answer="Demo walkthrough loaded.")

    store.record(
        TraceRecord(
            step=1,
            llm_text='{"type":"call_tool","tool":"read_file","args":{"path":"README.md"}}',
            llm_action=read_action,
            permission_verdict="allow",
            tool_result=ToolResult(success=True, output="# AI4SE Coding Agent Harness\n..."),
            feedback=Feedback(category="success", message="read_file succeeded", raw="success"),
            context_size=2,
        )
    )
    store.record(
        TraceRecord(
            step=2,
            llm_text=(
                '{"type":"call_tool","tool":"write_file",'
                '"args":{"path":".harness/demo-note.txt","content":"judge demo approved"}}'
            ),
            llm_action=write_action,
            permission_verdict="ask",
            hitl_status="pending",
            context_size=4,
        )
    )
    store.record(
        TraceRecord(
            step=3,
            llm_text='{"type":"done","answer":"Demo walkthrough loaded."}',
            llm_action=done_action,
            permission_verdict="allow",
            context_size=5,
        )
    )
    store.flush()

    manager = HITLManager(store=HITLStore(store_file))
    manager.requests = []
    request = manager.create_request(
        write_action,
        "demo write approval",
        context=[
            {"role": "system", "content": "You are a coding agent."},
            {"role": "user", "content": "Create the demo note after approval."},
        ],
        step=2,
    )
    return {"trace_path": str(trace_file), "store_path": str(store_file), "request_id": request.id}
