from dataclasses import dataclass


@dataclass
class RunResult:
    answer: str
    halt_reason: str | None
    steps: int
    trace_path: str | None = None
