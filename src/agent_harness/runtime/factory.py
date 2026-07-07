from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
from agent_harness.credentials.manager import CredentialManager
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.openai import OpenAILLM
from agent_harness.models import AgentAction


def build_harness(config: HarnessConfig, credential_manager=None) -> Harness:
    llm_provider = config.llm.get("provider", "mock")
    if llm_provider == "mock":
        llm = MockLLM([LLMResponse("done", AgentAction(type="done"))])
    elif llm_provider == "openai":
        manager = credential_manager or CredentialManager()
        llm = OpenAILLM(
            api_key=manager.get() or "",
            model=config.llm.get("model", "gpt-4"),
            base_url=config.llm.get("base_url"),
            temperature=float(config.llm.get("temperature", 0.7)),
        )
    else:
        raise ValueError(f"Unsupported provider for local runtime: {llm_provider}")
    return Harness(llm=llm, max_steps=config.max_steps, config=config.model_dump())
