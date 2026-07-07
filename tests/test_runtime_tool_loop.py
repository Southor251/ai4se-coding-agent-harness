from agent_harness.agent.loop import agent_loop
from agent_harness.config.loader import HarnessConfig
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction
from agent_harness.runtime.factory import build_harness
from agent_harness.hitl.store import HITLStore


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


def test_runtime_permission_ask_creates_hitl_request(tmp_path):
    target = tmp_path / "note.txt"
    harness = build_harness(
        HarnessConfig(
            workspace_root=str(tmp_path),
            permission={
                "rules": [
                    {
                        "name": "ask writes",
                        "pattern": ".*",
                        "verdict": "ask",
                        "rule_type": "path",
                    }
                ]
            },
        )
    )
    harness.llm.responses = [
        LLMResponse(
            "write",
            AgentAction(
                type="call_tool",
                tool="write_file",
                args={"path": str(target), "content": "hello"},
            ),
        ),
        LLMResponse("done", AgentAction(type="done")),
    ]

    agent_loop("write note", harness)

    assert not target.exists()
    assert len(harness.hitl.requests) == 1
    assert harness.hitl.requests[0].status == "pending"


def test_runtime_permission_ask_persists_hitl_request(tmp_path):
    target = tmp_path / "note.txt"
    store_path = tmp_path / "requests.json"
    harness = build_harness(
        HarnessConfig(
            workspace_root=str(tmp_path),
            permission={
                "rules": [
                    {
                        "name": "ask writes",
                        "pattern": ".*",
                        "verdict": "ask",
                        "rule_type": "path",
                    }
                ]
            },
        ),
        hitl_store_path=str(store_path),
    )
    harness.llm.responses = [
        LLMResponse(
            "write",
            AgentAction(
                type="call_tool",
                tool="write_file",
                args={"path": str(target), "content": "hello"},
            ),
        ),
        LLMResponse("done", AgentAction(type="done")),
    ]

    agent_loop("write note", harness)

    requests = HITLStore(store_path).load()
    assert len(requests) == 1
    assert requests[0].status == "pending"
    assert requests[0].action.tool == "write_file"
