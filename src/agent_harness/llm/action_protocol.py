import json
from typing import Any

from agent_harness.models import AgentAction


VALID_TYPES = {"call_tool", "done", "take_note"}


def parse_agent_action(text: str) -> AgentAction:
    text = _normalize_action_text(text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = _extract_json_object(text)
        if payload is None:
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
    return _parse_done(payload)


def action_protocol_prompt(menu: list[dict]) -> str:
    tool_details = _format_tool_details(menu)
    return (
        "Respond with exactly one JSON object and no prose. "
        'Allowed action forms: {"type":"done","answer":"..."}, '
        '{"type":"take_note","note":"..."}, '
        '{"type":"call_tool","tool":"tool_name","args":{...}}. '
        f"Available tools: {tool_details}."
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


def _parse_done(payload: dict[str, Any]) -> AgentAction:
    answer = payload.get("answer")
    if answer is not None and not isinstance(answer, str):
        return _invalid("done action answer must be a string")
    return AgentAction(type="done", answer=answer)


def _invalid(message: str) -> AgentAction:
    return AgentAction(type="invalid", args={"error": message})


def _normalize_action_text(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```") or not stripped.endswith("```"):
        return stripped
    lines = stripped.splitlines()
    if len(lines) < 3:
        return stripped
    opening = lines[0].strip().lower()
    if opening not in {"```", "```json"}:
        return stripped
    return "\n".join(lines[1:-1]).strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    for start, char in enumerate(text):
        if char != "{":
            continue
        candidate = _balanced_json_candidate(text, start)
        if candidate is None:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _balanced_json_candidate(text: str, start: int) -> str | None:
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _format_tool_details(menu: list[dict]) -> str:
    if not menu:
        return "none"
    details = []
    for tool in menu:
        name = tool.get("name", "?")
        args_schema = tool.get("args_schema") or {}
        if args_schema:
            args = ", ".join(f"{key}: {value}" for key, value in args_schema.items())
            details.append(f"{name} args {{{args}}}")
        else:
            details.append(str(name))
    return "; ".join(details)
