from agent_harness.agent.harness import Harness


def agent_loop(goal: str, H: Harness) -> str:
    H.context = [{"role": "system", "content": H.system_prompt}]
    H.context.append({"role": "user", "content": goal})
    H.halt_reason = None
    answer = ""
    while H.step < H.max_steps:
        H.step += 1
        menu = []
        if H.tools:
            menu = [{"name": t.name, "description": t.description} for t in H.tools.list()]
        response = H.llm.call(H.context, menu)
        H.context.append({"role": "assistant", "content": response.text})
        if response.action.type == "done":
            answer = response.text
            H.halt_reason = "done"
            break
        elif response.action.type == "call_tool":
            if H.tools and response.action.tool:
                tool = H.tools.get(response.action.tool)
                if tool:
                    args = response.action.args or {}
                    path = args.get("path")
                    if H.scope and path:
                        scope_verdict = H.scope.check(str(path))
                        if scope_verdict.decision != "inside":
                            H.context.append(
                                {
                                    "role": "user",
                                    "content": f"Action blocked by scope: {scope_verdict.decision}",
                                }
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
                            continue
                    result = tool.run(**(response.action.args or {}))
                    observation = str(result.output if result.success else result.error)
                    H.context.append({"role": "user", "content": observation})
                    if H.feedback:
                        feedback = H.feedback.from_tool_result(result)
                        H.feedback_events.append(feedback)
                        H.context.append(
                            {"role": "user", "content": H.feedback.format_for_context(feedback)}
                        )
        elif response.action.type == "take_note":
            if H.memory and response.action.note:
                H.memory.write(response.action.note)
    if H.halt_reason is None and H.step >= H.max_steps:
        H.halt_reason = "max_steps"
    return answer
