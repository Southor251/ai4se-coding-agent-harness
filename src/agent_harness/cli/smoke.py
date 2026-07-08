from pathlib import Path

from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.governance.hitl import HITLManager
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.governance.scope import ScopeGuard
from agent_harness.hitl.store import HITLStore
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, PermissionRule
from agent_harness.runtime.factory import _default_safe_tools
from agent_harness.trace.store import TraceStore


def run_hitl_write_smoke(
    workspace: str = ".harness/smoke-workspace",
    store: str = ".harness/hitl/requests.json",
    trace: str = ".harness/runs/hitl-write-smoke.jsonl",
) -> list[str]:
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    store_path = Path(store)
    trace_path = Path(trace)
    target = workspace_path / "agent_smoke.txt"

    policy = PermissionPolicy()
    policy.add_rule(
        PermissionRule(
            name="ask before writes",
            pattern=".*",
            verdict="ask",
            rule_type="path",
        )
    )
    harness = Harness(
        llm=MockLLM(
            [
                LLMResponse(
                    "request write",
                    AgentAction(
                        type="call_tool",
                        tool="write_file",
                        args={"path": str(target), "content": "smoke ok\n"},
                    ),
                )
            ]
        ),
        tools=_default_safe_tools(),
        permission=policy,
        scope=ScopeGuard(str(workspace_path)),
        hitl=HITLManager(store=HITLStore(store_path)),
        feedback=FeedbackSensor(),
        trace=TraceStore(trace_path),
        max_steps=1,
    )

    agent_loop("create a smoke file", harness)
    pending = [request for request in harness.hitl.requests if request.status == "pending"]
    request_id = pending[-1].id if pending else "(none)"
    approve_command = (
        "agent-harness hitl approve "
        f"{request_id} --continue --store {store_path}"
    )
    return [
        "hitl write smoke",
        f"workspace: {workspace_path}",
        f"store: {store_path}",
        f"trace: {trace_path}",
        f"target_exists: {'yes' if target.exists() else 'no'}",
        f"pending_request: {request_id}",
        f"approve_command: {approve_command}",
    ]


def add_smoke_parser(subparsers):
    parser = subparsers.add_parser("smoke", help="run deterministic smoke workflows")
    smoke_subparsers = parser.add_subparsers(dest="smoke_command")

    hitl_write = smoke_subparsers.add_parser("hitl-write", help="create a pending write request")
    hitl_write.add_argument("--workspace", default=".harness/smoke-workspace")
    hitl_write.add_argument("--store", default=".harness/hitl/requests.json")
    hitl_write.add_argument("--trace", default=".harness/runs/hitl-write-smoke.jsonl")
    hitl_write.set_defaults(handler=_hitl_write)


def _hitl_write(args) -> int:
    for line in run_hitl_write_smoke(args.workspace, args.store, args.trace):
        print(line)
    return 0
