from agent_harness.cli.main import main
from agent_harness.cli.smoke import run_hitl_write_smoke


def test_hitl_write_smoke_creates_pending_request(tmp_path):
    workspace = tmp_path / "workspace"
    store = tmp_path / "requests.json"
    trace = tmp_path / "trace.jsonl"

    lines = run_hitl_write_smoke(str(workspace), str(store), str(trace))

    assert workspace.exists()
    assert store.exists()
    assert trace.exists()
    assert not (workspace / "agent_smoke.txt").exists()
    assert any("pending_request:" in line for line in lines)
    assert any("approve_command:" in line for line in lines)


def test_smoke_cli_hitl_write(capsys, tmp_path):
    exit_code = main(
        [
            "smoke",
            "hitl-write",
            "--workspace",
            str(tmp_path / "workspace"),
            "--store",
            str(tmp_path / "requests.json"),
            "--trace",
            str(tmp_path / "trace.jsonl"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "pending_request:" in captured.out
    assert "approve_command:" in captured.out
