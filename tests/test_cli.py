from agent_harness.cli.main import main
import agent_harness.cli.credentials as credentials_cli


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


def test_cli_credentials_update_prompt_hides_secret(monkeypatch, capsys):
    updated = {}

    class FakeCredentialManager:
        def update(self, secret):
            updated["secret"] = secret

    monkeypatch.setattr(credentials_cli, "CredentialManager", FakeCredentialManager)
    monkeypatch.setattr(credentials_cli.getpass, "getpass", lambda prompt: "sample-token")

    exit_code = main(["credentials", "update", "--prompt"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert updated["secret"] == "sample-token"
    assert "configured" in captured.out
    assert "sample-token" not in captured.out
