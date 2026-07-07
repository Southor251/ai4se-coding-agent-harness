from agent_harness.feedback.classifier import classify_feedback
from agent_harness.models import Feedback, ToolResult


class FeedbackSensor:
    def from_tool_result(self, result: ToolResult) -> Feedback:
        category = classify_feedback(result.output, result.success, result.error)
        return Feedback(
            category=category,
            message=self._message_for(category),
            raw=result.output or result.error or "",
        )

    def format_for_context(self, feedback: Feedback) -> str:
        return f"Feedback[{feedback.category}]: {feedback.message}"

    def _message_for(self, category: str) -> str:
        messages = {
            "success": "operation succeeded",
            "syntax": "syntax issue detected",
            "assertion": "assertion failure detected",
            "timeout": "timeout detected",
            "tool_error": "tool error detected",
        }
        return messages.get(category, "tool error detected")

