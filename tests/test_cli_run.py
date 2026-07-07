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
