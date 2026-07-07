from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction


def test_invalid_action_feedback_enters_context():
    mock = MockLLM(
        [
            LLMResponse(
                text="not json",
                action=AgentAction(type="invalid", args={"error": "Expected valid JSON"}),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=mock, max_steps=3)

    agent_loop("test", harness)

    assert any("Invalid action" in message["content"] for message in harness.context)
