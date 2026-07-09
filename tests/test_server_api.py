from agent_harness.web.demo_data import ensure_demo_trace
from agent_harness.server.api import load_console_payload, static_app_available


def test_load_console_payload_reads_trace_and_hitl(tmp_path):
    trace_path = tmp_path / "demo.jsonl"
    store_path = tmp_path / "requests.json"
    ensure_demo_trace(str(trace_path), str(store_path))

    payload = load_console_payload(str(trace_path), str(store_path))

    assert payload["summary"]["steps"] == 3
    assert payload["timeline"][1]["state"] == "pending"
    assert payload["hitl"][0]["status"] == "pending"


def test_static_app_assets_are_available():
    assets = static_app_available()

    assert assets["available"] is True
    assert {"index.html", "styles.css", "app.js"}.issubset(set(assets["files"]))
