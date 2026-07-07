# Task 0.1: Create project skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/agent_harness/__init__.py`
- Create: `src/agent_harness/cli/__init__.py`
- Create: `tests/__init__.py`
- Create: `Makefile`
- Create: `.gitignore`

**Goal:** Set up a Python 3.12 project with setuptools, dependency declarations, and CLI entry point.

**Dependencies:** None (first task)

**Verification:** `python -c "import agent_harness"` does not error

## Implementation Details

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "agent-harness"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai>=1.0",
    "keyring>=24.0",
    "streamlit>=1.28",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.scripts]
agent-harness = "agent_harness.cli.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### src/agent_harness/__init__.py

```python
"""A teaching-demo Coding Agent Harness."""
```

### src/agent_harness/cli/__init__.py

```python
"""CLI entry point package."""
```

### tests/__init__.py

Empty file.

### Makefile

```makefile
.PHONY: test lint clean web demo

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

clean:
	rm -rf .harness/trace/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/

web:
	streamlit run src/agent_harness/web/theater.py

demo:
	python -m demo.demo_guardrail
	python -m demo.demo_feedback
	python -m demo.demo_scope
```

### .gitignore

See `.gitignore` (already exists — ensure it covers: `.env`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `.pytest_cache/`, `.harness/`)

## TDD Steps

1. Write the failing test first: `tests/test_import.py` with `import agent_harness; assert True`
2. Run: `pytest tests/ -v` → FAIL (package not found)
3. Create all files above
4. Run: `pip install -e .`
5. Run: `pytest tests/ -v` → PASS
6. Commit