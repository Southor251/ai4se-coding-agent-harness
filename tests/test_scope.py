"""Tests for ScopeGuard path fencing."""

from pathlib import Path

from agent_harness.governance.scope import ScopeGuard


def test_inside_workspace():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        guard = ScopeGuard(workspace_root=tmp)
        test_file = Path(tmp) / "test.txt"
        test_file.write_text("hello")
        verdict = guard.check(str(test_file))
        assert verdict.decision == "inside"


def test_outside_workspace():
    import tempfile

    with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as outside:
        guard = ScopeGuard(workspace_root=workspace)
        outside_file = Path(outside) / "outside.txt"
        outside_file.write_text("outside")
        verdict = guard.check(str(outside_file))
        assert verdict.decision == "outside"


def test_sensitive_path():
    import tempfile

    with tempfile.TemporaryDirectory() as workspace:
        guard = ScopeGuard(workspace_root=workspace)
        policy_file = Path(workspace) / ".env"
        policy_file.write_text("placeholder")
        verdict = guard.check(str(policy_file))
        assert verdict.decision == "sensitive"


def test_workspace_escape_is_outside():
    import tempfile

    with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as outside:
        guard = ScopeGuard(workspace_root=workspace)
        outside_file = Path(outside) / "outside.txt"
        outside_file.write_text("outside")
        verdict = guard.check(str(Path(workspace) / ".." / Path(outside).name / "outside.txt"))
        assert verdict.decision == "outside"
