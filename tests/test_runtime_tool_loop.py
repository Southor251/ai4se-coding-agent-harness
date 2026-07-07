from agent_harness.agent.loop import agent_loop
from agent_harness.config.loader import HarnessConfig
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction
from agent_harness.runtime.factory import build_harness


def test_runtime_harness_can_read_scoped_file(tmp_path):
    target = tmp_path / "note.txt"
    target.write_text("hello", encoding="utf-8")
    harness = build_harness(HarnessConfig(workspace_root=str(tmp_path)))
    harness.llm.responses = [
        LLMResponse(
            "read",
            AgentAction(type="call_tool", tool="read_file", args={"path": str(target)}),
        ),
        LLMResponse("done", AgentAction(type="done")),
    ]

    agent_loop("read note", harness)

    assert any(message["content"] == "hello" for message in harness.context)
