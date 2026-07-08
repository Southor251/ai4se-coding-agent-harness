from agent_harness.llm.action_protocol import action_protocol_prompt, parse_agent_action


def test_parse_done_action_json():
    action = parse_agent_action('{"type": "done"}')

    assert action.type == "done"


def test_parse_done_action_with_answer():
    action = parse_agent_action('{"type": "done", "answer": "finished"}')

    assert action.type == "done"
    assert action.answer == "finished"


def test_parse_fenced_json_action():
    action = parse_agent_action('```json\n{"type": "done", "answer": "finished"}\n```')

    assert action.type == "done"
    assert action.answer == "finished"


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


def test_action_protocol_prompt_includes_tool_arg_schema():
    prompt = action_protocol_prompt(
        [
            {
                "name": "write_file",
                "description": "Write content to file",
                "args_schema": {"path": "target path", "content": "file content"},
            }
        ]
    )

    assert "write_file" in prompt
    assert "path" in prompt
    assert "content" in prompt
