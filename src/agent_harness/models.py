from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AgentAction:
    type: Literal["call_tool", "done", "take_note", "invalid"]
    tool: str | None = None
    args: dict | None = None
    note: str | None = None
    answer: str | None = None
    changed_code: bool = False


@dataclass
class ToolResult:
    success: bool
    output: str = ""
    error: str | None = None
    files_changed: list[str] = field(default_factory=list)


@dataclass
class TraceRecord:
    step: int
    llm_text: str
    llm_action: AgentAction
    permission_verdict: Literal["allow", "ask", "deny"]
    hitl_status: Literal["pending", "approved", "denied", "timed_out"] | None = None
    tool_result: ToolResult | None = None
    feedback: "Feedback | None" = None
    context_size: int = 0
    timestamp: float = 0.0


@dataclass
class Feedback:
    category: Literal["syntax", "assertion", "timeout", "tool_error", "success"]
    message: str
    raw: str


@dataclass
class HITLRequest:
    id: str
    action: AgentAction
    reason: str
    status: Literal["pending", "approved", "denied", "timed_out"]
    created_at: float
    decided_by: Literal["human", "auto_deny", "timeout"] | None = None
    resolved_at: float | None = None
    context: list[dict] | None = None
    step: int = 0


@dataclass
class PermissionRule:
    name: str
    pattern: str
    verdict: Literal["allow", "ask", "deny"]
    rule_type: Literal["path", "command", "regex"]
    tools: list[str] = field(default_factory=list)


@dataclass
class ScopeVerdict:
    decision: Literal["inside", "outside", "sensitive"]
    normalized_path: str
    workspace_root: str
