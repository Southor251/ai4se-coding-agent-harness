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
    return answer