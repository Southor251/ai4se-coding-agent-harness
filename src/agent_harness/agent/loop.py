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
                    result = tool.run(**(response.action.args or {}))
                    H.context.append(
                        {"role": "user", "content": str(result.output if result.success else result.error)}
                    )
        elif response.action.type == "take_note":
            if H.memory and response.action.note:
                H.memory.write(response.action.note)
    if H.halt_reason is None and H.step >= H.max_steps:
        H.halt_reason = "max_steps"
    return answer
