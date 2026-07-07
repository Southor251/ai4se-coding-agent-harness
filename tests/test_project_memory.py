from agent_harness.memory.project import ProjectMemory


def test_project_memory_writes_append_only_notes(tmp_path):
    memory = ProjectMemory(tmp_path)

    memory.write("first")
    memory.write("second")

    assert memory.read_all() == ["first", "second"]
    assert (tmp_path / ".harness" / "memory" / "project.md").exists()


def test_project_memory_ignores_empty_notes(tmp_path):
    memory = ProjectMemory(tmp_path)

    memory.write("")

    assert memory.read_all() == []
