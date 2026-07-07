def classify_feedback(output: str = "", success: bool = False, error: str | None = None) -> str:
    text = f"{output}\n{error or ''}".lower()
    if success:
        return "success"
    if "syntaxerror" in text or "syntax error" in text:
        return "syntax"
    if "assertionerror" in text or "assertion" in text:
        return "assertion"
    if "timed out" in text or "timeout" in text:
        return "timeout"
    return "tool_error"

