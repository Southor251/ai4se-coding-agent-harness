from agent_harness.hitl.store import HITLStore
from agent_harness.web.demo_data import ensure_demo_trace
from agent_harness.web.services import trace_summary, trace_timeline


def test_ensure_demo_trace_creates_trace_and_hitl_store(tmp_path):
    trace_path = tmp_path / "demo.jsonl"
    store_path = tmp_path / "requests.json"

    result = ensure_demo_trace(str(trace_path), str(store_path))

    assert result["trace_path"] == str(trace_path)
    assert result["store_path"] == str(store_path)
    assert result["request_id"]
    assert trace_summary(str(trace_path))["steps"] == 3
    assert any(row["state"] == "pending" for row in trace_timeline(str(trace_path)))
    requests = HITLStore(store_path).load()
    assert len(requests) == 1
    assert requests[0].id == result["request_id"]
    assert requests[0].status == "pending"
    assert requests[0].action.tool == "write_file"
