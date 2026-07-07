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