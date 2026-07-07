from agent_harness.cli.main import main
from agent_harness.cli.run import run_goal


def test_run_goal_returns_structured_result():
    result = run_goal("say done")

    assert result.answer == "done"
    assert result.halt_reason == "done"
    assert result.steps == 1


def test_run_command_executes_goal(capsys):
    exit_code = main(["run", "say done"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "done" in captured.out


def test_run_command_with_openai_config_without_key_exits_safely(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    config_path = tmp_path / "agent-harness.yaml"
    config_path.write_text(
        "\n".join(
            [
                "max_steps: 3",
                "llm:",
                "  provider: openai",
                "  model: custom-model",
                "  temperature: 0.2",
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(["run", "say done", "--config", str(config_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "API key not configured" in captured.out
