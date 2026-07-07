from agent_harness.llm.action_protocol import parse_agent_action


def test_parse_done_action_json():
    action = parse_agent_action('{"type": "done"}')

    assert action.type == "done"


def test_parse_call_tool_action_json():
    action = parse_agent_action(
        '{"type": "call_tool", "tool": "read_file", "args": {"path": "README.md"}}'
    )

    assert action.type == "call_tool"
    assert action.tool == "read_file"
    assert action.args == {"path": "README.md"}


def test_parse_take_note_action_json():
    action = parse_agent_action('{"type": "take_note", "note": "remember this"}')

    assert action.type == "take_note"
    assert action.note == "remember this"


def test_invalid_json_becomes_invalid_action():
    action = parse_agent_action("not json")

    assert action.type == "invalid"
    assert "valid JSON" in action.args["error"]


def test_call_tool_without_tool_is_invalid():
    action = parse_agent_action('{"type": "call_tool", "args": {}}')

    assert action.type == "invalid"
    assert "tool" in action.args["error"]
