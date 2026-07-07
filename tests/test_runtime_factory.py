from agent_harness.agent.harness import Harness
from agent_harness.config.loader import HarnessConfig
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
