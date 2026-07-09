from scripts.verify_web_ui import validate_body


def test_validate_body_accepts_expected_text():
    assert validate_body("<html>Agent Harness Console</html>", "Agent Harness Console") is True


def test_validate_body_accepts_streamlit_shell_without_expected_text():
    assert validate_body("<html><script src='/static/js/streamlit.js'></script></html>", None) is True


def test_validate_body_rejects_unrelated_body():
    assert validate_body("<html>not the app</html>", None) is False
