from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction


def build_harness(config: HarnessConfig) -> Harness:
    llm_provider = config.llm.get("provider", "mock")
    if llm_provider != "mock":
        raise ValueError(f"Unsupported provider for local runtime: {llm_provider}")
    llm = MockLLM([LLMResponse("done", AgentAction(type="done"))])
    return Harness(llm=llm, max_steps=config.max_steps, config=config.model_dump())
