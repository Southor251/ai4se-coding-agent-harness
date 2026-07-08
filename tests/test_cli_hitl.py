from agent_harness.cli.main import main
from agent_harness.hitl.store import HITLStore
from agent_harness.models import AgentAction
from agent_harness.governance.hitl import HITLManager


def _create_request(store_path, action=None):
    manager = HITLManager(store=HITLStore(store_path))
    return manager.create_request(
        action or AgentAction(type="call_tool", tool="write_file", args={"path": "note.txt", "content": "hello"}),
        "review",
    )


def test_hitl_list_prints_pending_request(tmp_path, capsys):
    store_path = tmp_path / "requests.json"
    request = _create_request(store_path)

    exit_code = main(["hitl", "list", "--store", str(store_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert request.id in captured.out
    assert "pending" in captured.out
    assert "write_file" in captured.out


def test_hitl_deny_updates_store(tmp_path, capsys):
    store_path = tmp_path / "requests.json"
    request = _create_request(store_path)

    exit_code = main(["hitl", "deny", request.id, "--store", str(store_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "denied" in captured.out
    assert HITLStore(store_path).load()[0].status == "denied"


def test_hitl_approve_executes_request(tmp_path, capsys):
    store_path = tmp_path / "requests.json"
    target = tmp_path / "note.txt"
    request = _create_request(
        store_path,
        AgentAction(
            type="call_tool",
            tool="write_file",
            args={"path": str(target), "content": "hello"},
        ),
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(f"workspace_root: {tmp_path}\nllm:\n  provider: mock\n", encoding="utf-8")

    exit_code = main(
        [
            "hitl",
            "approve",
            request.id,
            "--config",
            str(config_path),
            "--store",
            str(store_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Written" in captured.out
    assert target.read_text(encoding="utf-8") == "hello"
    assert HITLStore(store_path).load()[0].status == "approved"


def test_hitl_approve_continue_resumes_after_tool_result(tmp_path, capsys):
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
        context=[
            {"role": "system", "content": "You are a coding agent."},
            {"role": "user", "content": "write note"},
        ],
        step=1,
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(f"workspace_root: {tmp_path}\nllm:\n  provider: mock\n", encoding="utf-8")

    exit_code = main(
        [
            "hitl",
            "approve",
            request.id,
            "--config",
            str(config_path),
            "--store",
            str(store_path),
            "--continue",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert target.read_text(encoding="utf-8") == "hello"
    assert "halt_reason=done" in captured.out
    assert HITLStore(store_path).load()[0].status == "approved"


def test_hitl_approve_unknown_request_returns_error(tmp_path, capsys):
    store_path = tmp_path / "requests.json"

    exit_code = main(["hitl", "approve", "missing", "--store", str(store_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "not found" in captured.out
