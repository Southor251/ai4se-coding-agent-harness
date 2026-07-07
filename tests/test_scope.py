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
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/etc/passwd")
    assert verdict.decision == "outside"


def test_sensitive_path():
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/workspace/.git/config")
    assert verdict.decision == "sensitive"


def test_sensitive_etc():
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/workspace/../etc/passwd")
    assert verdict.decision in ("outside", "sensitive")
