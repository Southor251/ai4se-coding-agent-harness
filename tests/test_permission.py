from agent_harness.governance.permission import PermissionPolicy
from agent_harness.models import PermissionRule, AgentAction


def test_default_allow():
    p = PermissionPolicy()
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "safe-list"})
    assert p.check(action) == "allow"


def test_deny_blocked_command_fixture():
    p = PermissionPolicy()
    p.add_rule(
        PermissionRule(
            name="deny blocked command fixture",
            pattern="blocked-command",
            verdict="deny",
            rule_type="command",
        )
    )
    action = AgentAction(
        type="call_tool",
        tool="run_shell",
        args={"command": "blocked-command --target workspace"},
    )
    assert p.check(action) == "deny"


def test_allow_safe():
    p = PermissionPolicy()
    p.add_rule(
        PermissionRule(
            name="deny blocked command fixture",
            pattern="blocked-command",
            verdict="deny",
            rule_type="command",
        )
    )
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "safe-list --all"})
    assert p.check(action) == "allow"


def test_deny_priority():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="allow all", pattern=".*", verdict="allow", rule_type="command"))
    p.add_rule(
        PermissionRule(
            name="deny blocked command fixture",
            pattern="blocked-command",
            verdict="deny",
            rule_type="command",
        )
    )
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "blocked-command file"})
    assert p.check(action) == "deny"


def test_ask():
    p = PermissionPolicy()
    p.add_rule(PermissionRule(name="ask review", pattern="review-command", verdict="ask", rule_type="command"))
    action = AgentAction(type="call_tool", tool="run_shell", args={"command": "review-command file"})
    assert p.check(action) == "ask"
