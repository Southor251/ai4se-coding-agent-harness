from dataclasses import dataclass, field
from typing import Any
from agent_harness.llm.interface import LLMInterface


@dataclass
class Harness:
    llm: LLMInterface
    tools: Any = None
    permission: Any = None
    feedback: Any = None
    trace: Any = None
    memory: Any = None
    config: dict = field(default_factory=dict)
    system_prompt: str = "You are a coding agent."
    max_steps: int = 50
    step: int = 0