import time

from agent_harness.agent.harness import Harness
from agent_harness.models import TraceRecord


def _record_trace(
    H: Harness,
    *,
    step: int,
    response,
    permission_verdict: str,
    tool_result=None,
    feedback=None,
    hitl_status=None,
) -> None:
    if not H.trace:
        return
    H.trace.record(
        TraceRecord(
            step=step,
            llm_text=response.text,
            llm_action=response.action,
            permission_verdict=permission_verdict,
            hitl_status=hitl_status,
            tool_result=tool_result,
            feedback=feedback,
            context_size=len(H.context),
            timestamp=time.time(),
        )
    )


def _scope_target(args: dict) -> str | None:
    for key in ("path", "pattern"):
        value = args.get(key)
        if value:
            return str(value)
    return None


def agent_loop(goal: str, H: Harness) -> str:
    H.step = 0
    H.context = [{"role": "system", "content": H.system_prompt}]
    H.context.append({"role": "user", "content": goal})
    H.halt_reason = None
    H.feedback_events = []
    answer = ""
    while H.step < H.max_steps:
        H.step += 1
        permission_verdict = "allow"
        tool_result = None
        feedback = None
        menu = []
        if H.tools:
            menu = [{"name": t.name, "description": t.description} for t in H.tools.list()]
        response = H.llm.call(H.context, menu)
        H.context.append({"role": "assistant", "content": response.text})
        if response.action.type == "done":
            answer = response.text
            H.halt_reason = "done"
            _record_trace(
                H,
                step=H.step,
                response=response,
                permission_verdict=permission_verdict,
            )
            break
        elif response.action.type == "call_tool":
            if H.tools and response.action.tool:
                tool = H.tools.get(response.action.tool)
                if tool:
                    args = response.action.args or {}
                    if H.scope and tool.name == "run_shell" and H.permission is None:
                        permission_verdict = "deny"
                        H.context.append(
                            {
                                "role": "user",
                                "content": "Action blocked by shell policy",
                            }
                        )
                        _record_trace(
                            H,
                            step=H.step,
                            response=response,
                            permission_verdict=permission_verdict,
                        )
                        continue
                    scope_target = _scope_target(args)
                    if H.scope and scope_target:
                        scope_verdict = H.scope.check(scope_target)
                        if scope_verdict.decision != "inside":
                            permission_verdict = "deny"
                            H.context.append(
                                {
                                    "role": "user",
                                    "content": f"Action blocked by scope: {scope_verdict.decision}",
                                }
                            )
                            _record_trace(
                                H,
                                step=H.step,
                                response=response,
                                permission_verdict=permission_verdict,
                            )
                            continue
                    if H.permission:
                        permission_verdict = H.permission.check(response.action)
                        if permission_verdict == "deny":
                            H.context.append(
                                {
                                    "role": "user",
                                    "content": "Action blocked by permission policy",
                                }
                            )
                            _record_trace(
                                H,
                                step=H.step,
                                response=response,
                                permission_verdict=permission_verdict,
                            )
                            continue
                        if permission_verdict == "ask":
                            if H.hitl:
                                H.hitl.create_request(response.action, "permission review required")
                            H.context.append(
                                {
                                    "role": "user",
                                    "content": "Action requires human approval",
                                }
                            )
                            _record_trace(
                                H,
                                step=H.step,
                                response=response,
                                permission_verdict=permission_verdict,
                                hitl_status="pending" if H.hitl else None,
                            )
                            continue
                    tool_result = tool.run(**(response.action.args or {}))
                    observation = str(tool_result.output if tool_result.success else tool_result.error)
                    H.context.append({"role": "user", "content": observation})
                    if H.feedback:
                        feedback = H.feedback.from_tool_result(tool_result)
                        H.feedback_events.append(feedback)
                        H.context.append(
                            {"role": "user", "content": H.feedback.format_for_context(feedback)}
                        )
                    _record_trace(
                        H,
                        step=H.step,
                        response=response,
                        permission_verdict=permission_verdict,
                        tool_result=tool_result,
                        feedback=feedback,
                    )
                else:
                    permission_verdict = "deny"
                    H.context.append(
                        {
                            "role": "user",
                            "content": f"Tool not found: {response.action.tool}",
                        }
                    )
                    _record_trace(
                        H,
                        step=H.step,
                        response=response,
                        permission_verdict=permission_verdict,
                    )
        elif response.action.type == "take_note":
            if H.memory and response.action.note:
                H.memory.write(response.action.note)
            _record_trace(
                H,
                step=H.step,
                response=response,
                permission_verdict=permission_verdict,
            )
    if H.halt_reason is None and H.step >= H.max_steps:
        H.halt_reason = "max_steps"
    if H.trace:
        H.trace.flush()
    return answer
