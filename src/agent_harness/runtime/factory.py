from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
from agent_harness.credentials.manager import CredentialManager
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.governance.hitl import HITLManager
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.governance.scope import ScopeGuard
from agent_harness.hitl.store import HITLStore
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.openai import OpenAILLM
from agent_harness.memory.project import ProjectMemory
from agent_harness.models import AgentAction, PermissionRule
from agent_harness.tools.builtin.edit_file import EditFileTool
from agent_harness.tools.builtin.read_file import ReadFileTool
from agent_harness.tools.builtin.run_test import RunTestTool
from agent_harness.tools.builtin.write_file import WriteFileTool
from agent_harness.tools.registry import ToolRegistry
from agent_harness.trace.store import TraceStore


DEFAULT_HITL_STORE_PATH = ".harness/hitl/requests.json"


def build_harness(
    config: HarnessConfig,
    credential_manager=None,
    trace_path: str | None = None,
    hitl_store_path: str | None = DEFAULT_HITL_STORE_PATH,
) -> Harness:
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
        permission=_permission_policy(config),
        scope=ScopeGuard(config.workspace_root),
        hitl=HITLManager(store=HITLStore(hitl_store_path)) if hitl_store_path else HITLManager(),
        feedback=FeedbackSensor(),
        trace=TraceStore(trace_path) if trace_path else None,
        memory=_project_memory(config),
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


def _permission_policy(config: HarnessConfig) -> PermissionPolicy | None:
    rules = config.permission.get("rules", [])
    if not rules:
        return None
    policy = PermissionPolicy()
    for rule in rules:
        policy.add_rule(
            PermissionRule(
                name=rule["name"],
                pattern=rule["pattern"],
                verdict=rule["verdict"],
                rule_type=rule["rule_type"],
            )
        )
    return policy


def _project_memory(config: HarnessConfig) -> ProjectMemory | None:
    if not config.memory.get("enabled", False):
        return None
    return ProjectMemory(config.workspace_root)
