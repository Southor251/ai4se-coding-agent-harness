from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
from agent_harness.llm.openai import OpenAILLM
from agent_harness.runtime.factory import build_harness
from agent_harness.runtime.result import RunResult


def test_run_result_captures_loop_summary():
    result = RunResult(answer="done", halt_reason="done", steps=1)

    assert result.answer == "done"
    assert result.halt_reason == "done"
    assert result.steps == 1
    assert result.trace_path is None


def test_build_harness_uses_safe_mock_default():
    harness = build_harness(HarnessConfig(max_steps=7))

    assert isinstance(harness, Harness)
    assert harness.max_steps == 7
    assert harness.llm.call([], []).action.type == "done"


class FakeCredentialManager:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def test_build_harness_supports_openai_provider_from_credentials():
    config = HarnessConfig(
        llm={
            "provider": "openai",
            "model": "custom-model",
            "base_url": "https://example.test/v1",
            "temperature": 0.2,
        }
    )

    harness = build_harness(config, credential_manager=FakeCredentialManager("sample-token"))

    assert isinstance(harness.llm, OpenAILLM)
    assert harness.llm.api_key == "sample-token"
    assert harness.llm.model == "custom-model"
    assert harness.llm.base_url == "https://example.test/v1"
    assert harness.llm.temperature == 0.2


def test_build_harness_registers_default_safe_tools():
    harness = build_harness(HarnessConfig())

    tool_names = {tool.name for tool in harness.tools.list()}

    assert {"read_file", "write_file", "edit_file", "run_test"}.issubset(tool_names)
    assert "run_shell" not in tool_names


def test_build_harness_adds_scope_and_feedback(tmp_path):
    config = HarnessConfig(workspace_root=str(tmp_path))

    harness = build_harness(config)

    assert harness.scope.check(str(tmp_path)).decision == "inside"
    assert harness.feedback is not None
