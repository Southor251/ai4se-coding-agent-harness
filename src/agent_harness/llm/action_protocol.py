import json
from typing import Any

from agent_harness.models import AgentAction


VALID_TYPES = {"call_tool", "done", "take_note"}


def parse_agent_action(text: str) -> AgentAction:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _invalid("Expected valid JSON action object")

    if not isinstance(payload, dict):
        return _invalid("Expected valid JSON object")

    action_type = payload.get("type")
    if action_type not in VALID_TYPES:
        return _invalid("Expected action type to be one of call_tool, done, take_note")

    if action_type == "call_tool":
        return _parse_call_tool(payload)
    if action_type == "take_note":
        return _parse_take_note(payload)
    return AgentAction(type="done")


def action_protocol_prompt(menu: list[dict]) -> str:
    tool_names = ", ".join(tool.get("name", "?") for tool in menu) or "none"
    return (
        "Respond with exactly one JSON object and no prose. "
        'Allowed action forms: {"type":"done"}, '
        '{"type":"take_note","note":"..."}, '
        '{"type":"call_tool","tool":"tool_name","args":{...}}. '
        f"Available tools: {tool_names}."
    )


def _parse_call_tool(payload: dict[str, Any]) -> AgentAction:
    tool = payload.get("tool")
    args = payload.get("args", {})
    if not isinstance(tool, str) or not tool:
        return _invalid("call_tool action requires a non-empty tool string")
    if not isinstance(args, dict):
        return _invalid("call_tool action requires args to be an object")
    return AgentAction(type="call_tool", tool=tool, args=args)


def _parse_take_note(payload: dict[str, Any]) -> AgentAction:
    note = payload.get("note")
    if not isinstance(note, str) or not note:
        return _invalid("take_note action requires a non-empty note string")
    return AgentAction(type="take_note", note=note)


def _invalid(message: str) -> AgentAction:
    return AgentAction(type="invalid", args={"error": message})
