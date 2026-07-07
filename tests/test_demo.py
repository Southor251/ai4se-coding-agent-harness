from demo.demo_feedback import run_demo as run_feedback_demo
from demo.demo_guardrail import run_demo as run_guardrail_demo
from demo.demo_scope import run_demo as run_scope_demo


def test_guardrail_demo_is_deterministic():
    result = run_guardrail_demo()

    assert result["status"] == "denied"
    assert result["tool_executed"] is False


def test_feedback_demo_is_deterministic():
    result = run_feedback_demo()

    assert result["status"] == "healed"
    assert result["feedback_category"] == "assertion"
    assert result["attempts"] == 2


def test_scope_demo_is_deterministic():
    result = run_scope_demo()

    assert result["status"] == "scope_denied"
    assert result["tool_executed"] is False
