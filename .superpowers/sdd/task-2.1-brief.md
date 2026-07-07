# Task 2.1 + 2.2: Harness dataclass + agent_loop base

**Files:**
- Create: `src/agent_harness/agent/__init__.py`
- Create: `src/agent_harness/agent/harness.py`
- Create: `src/agent_harness/agent/loop.py`
- Create: `tests/test_loop.py`

**Goal:** Harness holds all components. agent_loop runs the basic cycle: context → LLM → done.

**Dependencies:** T1.1 (models), T1.3 (MockLLM)

## Harness dataclass

```python
# src/agent_harness/agent/harness.py
from dataclasses import dataclass, field
from typing import Any
from agent_harness.llm.interface import LLMInterface

@dataclass
class Harness:
    llm: LLMInterface
    tools: Any = None          # ToolRegistry (T3)
    permission: Any = None     # PermissionPolicy (T4)
    feedback: Any = None       # FeedbackSensor (T5)
    trace: Any = None          # TraceStore (T6)
    memory: Any = None         # Scratchpad (T6.1)
    config: dict = field(default_factory=dict)
    system_prompt: str = "You are a coding agent."
    max_steps: int = 50
    step: int = 0
```

## agent_loop (basic)

```python
# src/agent_harness/agent/loop.py
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
```

## Tests

```python
# tests/test_loop.py
from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction

def test_harness_holds_llm():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock)
    assert H.llm is mock

def test_agent_loop_immediate_done():
    mock = MockLLM(responses=[LLMResponse(text="ok", action=AgentAction(type="done"))])
    H = Harness(llm=mock, max_steps=10)
    answer = agent_loop("test", H)
    assert answer == "ok"
    assert H.step == 1

def test_agent_loop_multiple_steps():
    r1 = LLMResponse(text="first", action=AgentAction(type="call_tool", tool="read_file"))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, max_steps=10)
    answer = agent_loop("test", H)
    assert H.step == 2

def test_agent_loop_max_steps():
    mock = MockLLM(responses=[])  # exhausted → auto-done
    H = Harness(llm=mock, max_steps=3)
    answer = agent_loop("test", H)
    assert H.step <= 3
```