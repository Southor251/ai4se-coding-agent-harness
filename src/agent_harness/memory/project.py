from pathlib import Path


class ProjectMemory:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.path = self.root / ".harness" / "memory" / "project.md"

    def write(self, note: str) -> None:
        normalized = note.strip()
        if not normalized:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"- {normalized}\n")

    def read_all(self) -> list[str]:
        if not self.path.exists():
            return []
        notes = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- "):
                notes.append(line[2:])
        return notes
