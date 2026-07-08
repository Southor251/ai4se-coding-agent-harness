from agent_harness.cli.run import run_goal
from agent_harness.config.loader import load_config_with_profile
from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.resume import approve_and_execute, approve_execute_and_continue
from agent_harness.hitl.store import HITLStore
from agent_harness.models import HITLRequest
from agent_harness.runtime.factory import build_harness
from agent_harness.runtime.result import RunResult
from agent_harness.tools.base import ToolResult
from agent_harness.trace.store import TraceStore
from agent_harness.web.theater import summarize_trace


DEFAULT_CONFIG_PATH = "config/agent-harness.yaml"
DEFAULT_PROFILE_PATH = "config/personal-harness.yaml"
DEFAULT_TRACE_PATH = ".harness/runs/latest.jsonl"
DEFAULT_HITL_STORE_PATH = ".harness/hitl/requests.json"


def run_task(
    goal: str,
    config_path: str = DEFAULT_CONFIG_PATH,
    profile_path: str | None = None,
    trace_path: str = DEFAULT_TRACE_PATH,
) -> RunResult:
    return run_goal(goal, config_path=config_path, profile_path=profile_path, trace_path=trace_path)


def trace_summary(trace_path: str = DEFAULT_TRACE_PATH) -> dict:
    return summarize_trace(TraceStore.load(trace_path))


def list_hitl_requests(store_path: str = DEFAULT_HITL_STORE_PATH) -> list[dict]:
    rows = []
    for request in HITLStore(store_path).load():
        rows.append(
            {
                "id": request.id,
                "status": request.status,
                "tool": request.action.tool or "",
                "reason": request.reason,
                "created_at": request.created_at,
                "resolved_at": request.resolved_at or "",
                "decided_by": request.decided_by or "",
            }
        )
    return rows


def approve_hitl_request(
    request_id: str,
    config_path: str = DEFAULT_CONFIG_PATH,
    profile_path: str | None = None,
    store_path: str = DEFAULT_HITL_STORE_PATH,
) -> ToolResult:
    config = load_config_with_profile(config_path, profile_path)
    harness = build_harness(config, hitl_store_path=store_path)
    return approve_and_execute(harness, request_id)


def approve_and_continue_hitl_request(
    request_id: str,
    config_path: str = DEFAULT_CONFIG_PATH,
    profile_path: str | None = None,
    store_path: str = DEFAULT_HITL_STORE_PATH,
) -> RunResult:
    config = load_config_with_profile(config_path, profile_path)
    harness = build_harness(config, hitl_store_path=store_path)
    return approve_execute_and_continue(harness, request_id)


def deny_hitl_request(request_id: str, store_path: str = DEFAULT_HITL_STORE_PATH) -> HITLRequest:
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.find(request_id)
    if request is None:
        raise ValueError(f"HITL request not found: {request_id}")
    if request.status != "pending":
        raise ValueError(f"HITL request is not pending: {request_id}")
    denied = manager.deny(request_id)
    if denied is None:
        raise ValueError(f"HITL request not found: {request_id}")
    return denied
