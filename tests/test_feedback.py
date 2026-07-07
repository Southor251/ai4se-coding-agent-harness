from agent_harness.feedback.classifier import classify_feedback
from agent_harness.feedback.heal import HealingState
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.models import ToolResult


def test_classify_success():
    assert classify_feedback(output="1 passed", success=True, error=None) == "success"


def test_classify_syntax_error():
    assert classify_feedback(output="SyntaxError: invalid syntax", success=False, error=None) == "syntax"


def test_classify_assertion_error():
    assert classify_feedback(output="AssertionError: expected value", success=False, error=None) == "assertion"


def test_classify_timeout():
    assert classify_feedback(output="", success=False, error="Command timed out") == "timeout"


def test_classify_tool_error():
    assert classify_feedback(output="unexpected failure", success=False, error=None) == "tool_error"


def test_feedback_sensor_builds_feedback_from_result():
    sensor = FeedbackSensor()
    feedback = sensor.from_tool_result(
        ToolResult(success=False, output="AssertionError: expected value", error=None)
    )

    assert feedback.category == "assertion"
    assert "assertion" in feedback.message
    assert "AssertionError" in feedback.raw


def test_feedback_sensor_formats_feedback_for_context():
    sensor = FeedbackSensor()
    feedback = sensor.from_tool_result(ToolResult(success=False, error="Command timed out"))

    assert sensor.format_for_context(feedback) == "Feedback[timeout]: timeout detected"


def test_healing_state_escalates_after_limit():
    state = HealingState(max_retries=2)

    assert not state.record_failure("assertion")
    assert state.record_failure("assertion")
    assert state.should_escalate


def test_healing_state_resets_on_success():
    state = HealingState(max_retries=1)
    state.record_failure("assertion")
    state.record_success()

    assert state.failures == 0
    assert not state.should_escalate
