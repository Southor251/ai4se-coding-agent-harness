from agent_harness.agent.loop import agent_loop
from agent_harness.agent.harness import Harness
from agent_harness.models import ToolResult
from agent_harness.runtime.result import RunResult


def approve_and_execute(harness: Harness, request_id: str) -> ToolResult:
    if not harness.hitl:
        return ToolResult(success=False, error="HITL manager not configured")
    request = harness.hitl.find(request_id)
    if request is None:
        return ToolResult(success=False, error=f"HITL request not found: {request_id}")
    if request.status != "pending":
        return ToolResult(success=False, error=f"HITL request is not pending: {request.status}")
    if not harness.tools or not request.action.tool:
        return ToolResult(success=False, error="Tool registry not configured")
    tool = harness.tools.get(request.action.tool)
    if tool is None:
        return ToolResult(success=False, error=f"Tool not found: {request.action.tool}")
    if harness.scope:
        scope_target = _scope_target(request.action.args or {})
        if scope_target:
            verdict = harness.scope.check(scope_target)
            if verdict.decision != "inside":
                return ToolResult(success=False, error=f"Action blocked by scope: {verdict.decision}")

    harness.hitl.approve(request_id)
    return tool.run(**(request.action.args or {}))


def approve_execute_and_continue(harness: Harness, request_id: str) -> RunResult:
    if not harness.hitl:
        return RunResult(answer="HITL manager not configured", halt_reason="hitl_error", steps=harness.step)
    request = harness.hitl.find(request_id)
    if request is None:
        return RunResult(answer=f"HITL request not found: {request_id}", halt_reason="hitl_error", steps=harness.step)
    result = approve_and_execute(harness, request_id)
    if not result.success:
        return RunResult(answer=result.error or "", halt_reason="tool_error", steps=harness.step)

    if request.context:
        harness.context = list(request.context)
    if request.step:
        harness.step = request.step
    observation = str(result.output)
    harness.context.append({"role": "user", "content": observation})
    if harness.feedback:
        feedback = harness.feedback.from_tool_result(result)
        harness.feedback_events.append(feedback)
        harness.context.append({"role": "user", "content": harness.feedback.format_for_context(feedback)})

    answer = agent_loop("", harness, resume=True)
    return RunResult(answer=answer, halt_reason=harness.halt_reason, steps=harness.step)


def _scope_target(args: dict) -> str | None:
    for key in ("path", "pattern"):
        value = args.get(key)
        if value:
            return str(value)
    return None
