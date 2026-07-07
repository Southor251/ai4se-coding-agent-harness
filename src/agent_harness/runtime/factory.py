from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
from agent_harness.credentials.manager import CredentialManager
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.governance.scope import ScopeGuard
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.openai import OpenAILLM
from agent_harness.models import AgentAction
from agent_harness.tools.builtin.edit_file import EditFileTool
from agent_harness.tools.builtin.read_file import ReadFileTool
from agent_harness.tools.builtin.run_test import RunTestTool
from agent_harness.tools.builtin.write_file import WriteFileTool
from agent_harness.tools.registry import ToolRegistry


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
    return Harness(
        llm=llm,
        tools=_default_safe_tools(),
        scope=ScopeGuard(config.workspace_root),
        feedback=FeedbackSensor(),
        max_steps=config.max_steps,
        config=config.model_dump(),
    )


def _default_safe_tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    registry.register(RunTestTool())
    return registry
