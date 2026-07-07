from agent_harness.agent.harness import Harness
from agent_harness.models import AgentAction, TraceRecord


def agent_loop(goal: str, H: Harness) -> str:
    context = [{"role": "system", "content": H.system_prompt}]
    context.append({"role": "user", "content": goal})
    answer = ""
    while H.step < H.max_steps:
        H.step += 1
        menu = []
        if H.tools:
            menu = [{"name": t.name, "description": t.description} for t in H.tools.list()]
        response = H.llm.call(context, menu)
        context.append({"role": "assistant", "content": response.text})
        if response.action.type == "done":
            answer = response.text
            break
        elif response.action.type == "call_tool":
            if H.tools and response.action.tool:
                tool = H.tools.get(response.action.tool)
                if tool:
                    result = tool.run(**(response.action.args or {}))
                    context.append({"role": "user", "content": str(result.output if result.success else result.error)})
        elif response.action.type == "take_note":
            if H.memory and response.action.note:
                H.memory.write(response.action.note)
    return answer