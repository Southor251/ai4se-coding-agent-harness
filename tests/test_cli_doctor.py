from agent_harness.cli.doctor import run_doctor
from agent_harness.cli.main import main


class FakeCredentialManager:
    def show_status(self):
        return "configured"


def test_doctor_reports_runtime_without_secret(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text(
        "\n".join(
            [
                f"workspace_root: {tmp_path.as_posix()}",
                "llm:",
                "  provider: openai",
                "  model: test-model",
                "  base_url: https://example.test/v1",
                "  temperature: 0.1",
                "permission:",
                "  rules:",
                "    - name: ask writes",
                "      pattern: .*",
                "      verdict: ask",
                "      rule_type: path",
                "memory:",
                "  enabled: true",
            ]
        ),
        encoding="utf-8",
    )

    lines = run_doctor(None, str(profile), credential_manager=FakeCredentialManager())

    text = "\n".join(lines)
    assert "agent-harness doctor" in text
    assert "provider: openai" in text
    assert "model: test-model" in text
    assert "base_url: https://example.test/v1" in text
    assert "credential: configured" in text
    assert "run_shell: disabled" in text
    assert "permission_rules: 1" in text
    assert "memory: enabled" in text
    assert "sample-token" not in text


def test_doctor_cli_prints_summary(capsys):
    exit_code = main(["doctor", "--profile", "config/personal-harness.yaml"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "agent-harness doctor" in captured.out
    assert "run_shell: disabled" in captured.out
