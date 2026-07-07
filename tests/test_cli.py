from agent_harness.cli.main import main


def test_cli_help(capsys):
    exit_code = main(["--help"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "agent-harness" in captured.out


def test_cli_credentials_show(capsys):
    exit_code = main(["credentials", "show"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "configured" in captured.out or "not configured" in captured.out
