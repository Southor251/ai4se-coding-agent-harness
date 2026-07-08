from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.store import HITLStore
from agent_harness.models import AgentAction
from agent_harness.web.services import (
    approve_hitl_request,
    deny_hitl_request,
    list_hitl_requests,
    run_task,
    trace_summary,
)


def test_run_task_returns_result_and_trace(tmp_path):
    trace_path = tmp_path / "trace.jsonl"

    result = run_task("say done", trace_path=str(trace_path))

    assert result.answer == "done"
    assert result.trace_path == str(trace_path)
    assert trace_path.exists()


def test_trace_summary_reads_trace_file(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    run_task("say done", trace_path=str(trace_path))

    summary = trace_summary(str(trace_path))

    assert summary["steps"] == 1


def test_list_and_deny_hitl_requests(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.create_request(AgentAction(type="call_tool", tool="read_file"), "review")

    rows = list_hitl_requests(str(store_path))
    result = deny_hitl_request(request.id, str(store_path))

    assert rows[0]["id"] == request.id
    assert rows[0]["status"] == "pending"
    assert result.status == "denied"
    assert HITLStore(store_path).load()[0].status == "denied"


def test_approve_hitl_request_executes_pending_action(tmp_path):
    store_path = tmp_path / "requests.json"
    target = tmp_path / "note.txt"
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.create_request(
        AgentAction(
            type="call_tool",
            tool="write_file",
            args={"path": str(target), "content": "hello"},
        ),
        "review",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(f"workspace_root: {tmp_path}\nllm:\n  provider: mock\n", encoding="utf-8")

    result = approve_hitl_request(request.id, config_path=str(config_path), store_path=str(store_path))

    assert result.success is True
    assert target.read_text(encoding="utf-8") == "hello"
    assert HITLStore(store_path).load()[0].status == "approved"
