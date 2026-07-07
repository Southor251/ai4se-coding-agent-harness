# Task 4.1: PermissionPolicy only

**Files:**
- Create: `src/agent_harness/governance/__init__.py`
- Create: `src/agent_harness/governance/permission.py`
- Create: `tests/test_permission.py`

**Goal:** PermissionPolicy with allow/ask/deny rules, deny priority.

**Dependencies:** T1.1 (models - PermissionRule, AgentAction)

## Implementation

```python
# src/agent_harness/governance/__init__.py
"""Governance module: permission, scope, HITL."""
```

```python
# src/agent_harness/governance/permission.py
import re
from agent_harness.models import PermissionRule, AgentAction

class PermissionPolicy:
    def __init__(self):
        self.rules: list[PermissionRule] = []

    def add_rule(self, rule: PermissionRule):
        self.rules.append(rule)

    def check(self, action: AgentAction) -> str:
        if not self.rules:
            return "allow"
        verdict = "allow"
        command = str(action.args.get("command", "")) if action.args else ""
        path = str(action.args.get("path", "")) if action.args else ""
        for rule in self.rules:
            matched = False
            if rule.rule_type == "command":
                matched = re.search(rule.pattern, command, re.IGNORECASE) is not None
            elif rule.rule_type == "path":
                matched = re.search(rule.pattern, path, re.IGNORECASE) is not None
            elif rule.rule_type == "regex":
                matched = bool(re.search(rule.pattern, command + " " + path))
            if matched:
                if rule.verdict == "deny":
                    return "deny"
                if rule.verdict == "ask":
                    verdict = "ask"
        return verdict
```

## Tests

```python
# tests/test_permission.py
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.models import PermissionRule, AgentAction

def test_default_allow():
    p = PermissionPolicy()
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "ls"})
    assert p.check(action) == "allow"

def test_deny_rm():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="deny rm", pattern="rm -rf", verdict="deny", rule_type="command"))
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "rm -rf /"})
    assert p.check(action) == "deny"

def test_allow_safe():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="deny rm", pattern="rm -rf", verdict="deny", rule_type="command"))
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "ls -la"})
    assert p.check(action) == "allow"

def test_deny_priority():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="allow all", pattern=".*", verdict="allow", rule_type="command"))
    p.add_rule(PermissionRule(name="deny rm", pattern="rm", verdict="deny", rule_type="command"))
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "rm file"})
    assert p.check(action) == "deny"

def test_ask():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="ask delete", pattern="del", verdict="ask", rule_type="command"))
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "del file"})
    assert p.check(action) == "ask"
```

## TDD
1. Write test_permission.py
2. Run → FAIL (import error)
3. Create governance/__init__.py + permission.py
4. Run → 5/5 PASS
5. Commit