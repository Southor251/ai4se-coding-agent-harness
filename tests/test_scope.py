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


def test_sensitive_directory_itself():
    import tempfile

    with tempfile.TemporaryDirectory() as workspace:
        guard = ScopeGuard(workspace_root=workspace)
        policy_dir = Path(workspace) / ".git"
        policy_dir.mkdir()
        verdict = guard.check(str(policy_dir))
        assert verdict.decision == "sensitive"


def test_workspace_escape_is_outside():
    import tempfile

    with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as outside:
        guard = ScopeGuard(workspace_root=workspace)
        outside_file = Path(outside) / "outside.txt"
        outside_file.write_text("outside")
        verdict = guard.check(str(Path(workspace) / ".." / Path(outside).name / "outside.txt"))
        assert verdict.decision == "outside"


def test_sibling_directory_with_same_prefix_is_outside():
    import tempfile

    with tempfile.TemporaryDirectory() as parent:
        workspace = Path(parent) / "work"
        sibling = Path(parent) / "work-sibling"
        workspace.mkdir()
        sibling.mkdir()
        sibling_file = sibling / "outside.txt"
        sibling_file.write_text("outside")

        guard = ScopeGuard(workspace_root=str(workspace))
        verdict = guard.check(str(sibling_file))

        assert verdict.decision == "outside"


def test_missing_workspace_root_treats_paths_as_outside(tmp_path):
    missing_root = tmp_path / "missing"
    child = missing_root / "child.txt"
    guard = ScopeGuard(workspace_root=str(missing_root))

    verdict = guard.check(str(child))

    assert verdict.decision == "outside"
