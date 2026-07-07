from agent_harness.agent.harness import Harness
from agent_harness.models import ToolResult


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

    harness.hitl.approve(request_id)
    return tool.run(**(request.action.args or {}))
