# Task 2.3 + 2.4 + 2.5 + 3.1: call_tool dispatch + ToolBase + ToolRegistry + MAX_STEPS + take_note

**Files:**
- Create: `src/agent_harness/tools/__init__.py`
- Create: `src/agent_harness/tools/base.py`
- Create: `src/agent_harness/tools/registry.py`
- Create: `tests/test_tools.py`
- Modify: `src/agent_harness/agent/loop.py`
- Create: `tests/test_loop_extended.py`

**Goal:** ToolBase, ToolRegistry, and extended loop with call_tool/take_note/MAX_STEPS.

**Dependencies:** T2.2 (basic loop)

## ToolBase

```python
# src/agent_harness/tools/base.py
from abc import ABC, abstractmethod
from agent_harness.models import ToolResult

class ToolBase(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        ...
```

## ToolRegistry

```python
# src/agent_harness/tools/registry.py
from agent_harness.tools.base import ToolBase

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolBase] = {}

    def register(self, tool: ToolBase):
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolBase | None:
        return self._tools.get(name)

    def list(self) -> list[ToolBase]:
        return list(self._tools.values())

    def unregister(self, name: str):
        self._tools.pop(name, None)
```

## Extended loop (loop.py)

Add to agent_loop after the basic done check:
```python
        elif action.type == "call_tool":
            if H.tools and action.tool:
                tool = H.tools.get(action.tool)
                if tool:
                    result = tool.run(**(action.args or {}))
                    context.append({"role": "user", "content": str(result.output if result.success else result.error)})
        elif action.type == "take_note":
            if H.memory and action.note:
                H.memory.write(action.note)
```

## Tests

```python
# tests/test_tools.py
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry
from agent_harness.models import ToolResult

class EchoTool(ToolBase):
    def __init__(self):
        super().__init__(name="echo", description="echoes input")
    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=str(kwargs.get("msg", "")))

def test_tool_base_abstract():
    import pytest
    with pytest.raises(TypeError):
        ToolBase(name="test")

def test_registry_register_list():
    t = EchoTool()
    reg = ToolRegistry()
    reg.register(t)
    assert len(reg.list()) == 1
    assert reg.list()[0].name == "echo"

def test_registry_get():
    t = EchoTool()
    reg = ToolRegistry()
    reg.register(t)
    assert reg.get("echo") is t
    assert reg.get("nonexistent") is None

def test_tool_run():
    t = EchoTool()
    result = t.run(msg="hello")
    assert result.success
    assert result.output == "hello"
```

```python
# tests/test_loop_extended.py
from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction, ToolResult
from agent_harness.tools.registry import ToolRegistry
from agent_harness.tools.base import ToolBase

class FakeTool(ToolBase):
    def __init__(self):
        super().__init__(name="echo", description="echo test")
    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=str(kwargs.get("msg", "")))

class FakeMemory:
    def __init__(self):
        self.notes = []
    def write(self, note):
        self.notes.append(note)

def test_call_tool_dispatch():
    reg = ToolRegistry()
    reg.register(FakeTool())
    r1 = LLMResponse(text="calling", action=AgentAction(type="call_tool", tool="echo", args={"msg": "hi"}))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, tools=reg, max_steps=10)
    answer = agent_loop("test", H)
    assert answer == "done"

def test_take_note():
    mem = FakeMemory()
    r1 = LLMResponse(text="note", action=AgentAction(type="take_note", note="remember this"))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, memory=mem, max_steps=10)
    agent_loop("test", H)
    assert "remember this" in mem.notes

def test_max_steps_enforced():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock, max_steps=3)
    agent_loop("test", H)
    assert H.step == 3
```