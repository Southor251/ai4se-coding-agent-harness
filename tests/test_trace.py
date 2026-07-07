from agent_harness.models import AgentAction, TraceRecord
from agent_harness.trace.store import TraceStore


def test_trace_store_records_jsonl(tmp_path):
    path = tmp_path / "trace.jsonl"
    store = TraceStore(path)

    store.record(
        TraceRecord(
            step=1,
            llm_text="done",
            llm_action=AgentAction(type="done"),
            permission_verdict="allow",
            context_size=2,
        )
    )

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert '"step": 1' in lines[0]


def test_trace_store_loads_records(tmp_path):
    path = tmp_path / "trace.jsonl"
    store = TraceStore(path)
    store.record(
        TraceRecord(
            step=1,
            llm_text="done",
            llm_action=AgentAction(type="done"),
            permission_verdict="allow",
        )
    )

    records = TraceStore.load(path)

    assert records[0]["step"] == 1
    assert records[0]["llm_action"]["type"] == "done"


def test_trace_store_skips_bad_lines(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_text("{bad json}\n{\"step\": 2}\n", encoding="utf-8")

    records = TraceStore.load(path)

    assert records == [{"step": 2}]
