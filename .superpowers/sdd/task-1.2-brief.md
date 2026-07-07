# Task 1.2 + 1.3: LLMInterface + MockLLM

**Files:**
- Create: `src/agent_harness/llm/__init__.py`
- Create: `src/agent_harness/llm/interface.py`
- Create: `src/agent_harness/llm/mock.py`
- Update: `tests/test_llm.py`

**Goal:** LLMInterface abstract base + MockLLM with preset response queue.

**Dependencies:** T1.1 (models.py with AgentAction, LLMResponse concept)

## LLMInterface

```python
# src/agent_harness/llm/interface.py
from abc import ABC, abstractmethod
from agent_harness.models import AgentAction

class LLMResponse:
    def __init__(self, text: str, action: AgentAction):
        self.text = text
        self.action = action

class LLMInterface(ABC):
    @abstractmethod
    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        ...
```

## MockLLM

```python
# src/agent_harness/llm/mock.py
from agent_harness.llm.interface import LLMInterface, LLMResponse

class MockLLM(LLMInterface):
    def __init__(self, responses: list[LLMResponse]):
        self.responses = responses
        self.call_count = 0

    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        if self.call_count >= len(self.responses):
            return LLMResponse(text="", action=AgentAction(type="done"))
        response = self.responses[self.call_count]
        self.call_count += 1
        return response
```

## Tests

```python
# tests/test_llm.py
import pytest
from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction

def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        LLMInterface()

def test_mock_llm_returns_preset():
    expected = LLMResponse(text="hello", action=AgentAction(type="done"))
    mock = MockLLM(responses=[expected])
    result = mock.call([], [])
    assert result.text == "hello"
    assert result.action.type == "done"

def test_mock_llm_consumes_queue():
    r1 = LLMResponse(text="first", action=AgentAction(type="call_tool", tool="read_file"))
    r2 = LLMResponse(text="second", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    assert mock.call([], []).text == "first"
    assert mock.call([], []).text == "second"

def test_mock_llm_done_when_exhausted():
    mock = MockLLM(responses=[])
    result = mock.call([], [])
    assert result.action.type == "done"
```