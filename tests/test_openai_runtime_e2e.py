import json

from agent_harness.agent.loop import agent_loop
from agent_harness.config.loader import HarnessConfig
from agent_harness.llm.openai import OpenAILLM
from agent_harness.runtime.factory import build_harness
from agent_harness.trace.store import TraceStore


class SequentialOpenAIResponse:
    def __init__(self, text):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": text})()})()]


class SequentialCompletions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SequentialOpenAIResponse(self.responses.pop(0))


class SequentialChat:
    def __init__(self, responses):
        self.completions = SequentialCompletions(responses)


class SequentialClient:
    def __init__(self, responses):
        self.chat = SequentialChat(responses)


def _action(payload):
    return json.dumps(payload)


def test_openai_backed_runtime_executes_tool_task_end_to_end(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    output = tmp_path / "output.txt"
    test_file = tmp_path / "test_generated.py"
    trace_path = tmp_path / "trace.jsonl"
    source.write_text("seed", encoding="utf-8")
    test_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    class Completed:
        returncode = 0
        stdout = "1 passed"
        stderr = ""

    monkeypatch.setattr(
        "agent_harness.tools.builtin.run_test.subprocess.run",
        lambda *args, **kwargs: Completed(),
    )

    client = SequentialClient(
        [
            f"```json\n{_action({'type': 'call_tool', 'tool': 'read_file', 'args': {'path': str(source)}})}\n```",
            _action(
                {
                    "type": "call_tool",
                    "tool": "write_file",
                    "args": {"path": str(output), "content": "generated"},
                }
            ),
            _action({"type": "call_tool", "tool": "run_test", "args": {"pattern": str(test_file)}}),
            _action({"type": "done", "answer": "task complete"}),
        ]
    )
    harness = build_harness(
        HarnessConfig(workspace_root=str(tmp_path), llm={"provider": "openai"}, max_steps=6),
        credential_manager=type("Creds", (), {"get": lambda self: "test-key"})(),
        trace_path=str(trace_path),
        hitl_store_path=None,
    )
    harness.llm = OpenAILLM(api_key="test-key", client=client)

    answer = agent_loop("read, write, and test", harness)

    records = TraceStore.load(trace_path)
    assert answer == "task complete"
    assert output.read_text(encoding="utf-8") == "generated"
    assert harness.halt_reason == "done"
    assert harness.step == 4
    assert [record["llm_action"]["type"] for record in records] == [
        "call_tool",
        "call_tool",
        "call_tool",
        "done",
    ]
    assert records[0]["tool_result"]["output"] == "seed"
    assert records[2]["feedback"]["category"] == "success"
    assert len(client.chat.completions.calls) == 4
