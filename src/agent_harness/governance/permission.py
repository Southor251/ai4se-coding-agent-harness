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