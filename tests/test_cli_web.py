from agent_harness.cli.main import main
from agent_harness.cli.web import theater_command


def test_theater_command_returns_launch_instruction():
    message = theater_command("trace.jsonl")

    assert "streamlit run" in message
    assert "trace.jsonl" in message


def test_web_command_prints_launch_instruction(capsys):
    exit_code = main(["web", "--trace", "trace.jsonl"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "streamlit run" in captured.out
