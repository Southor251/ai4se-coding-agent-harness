# Task 3.2–3.7 Report: 5 Built-in Tools

## Status: ✅ Done

| Item | Result |
|---|---|
| Tests written to `tests/test_tools.py` | 8 new test functions added |
| `pytest tests/test_tools.py` before impl | ❌ ModuleNotFoundError (expected) |
| `builtin/__init__.py` created | Empty package init |
| 5 tool files created | `read_file.py`, `write_file.py`, `edit_file.py`, `run_shell.py`, `run_test.py` |
| `pytest tests/test_tools.py -v` after impl | ✅ **12/12 passed** |
| `pytest tests/ -v` full suite | ✅ **34/34 passed** |

## Commit

```
c505ad5  Add 5 built-in tool classes (ReadFile, WriteFile, EditFile, RunShell, RunTest) and their tests
```

## Files Changed

- `tests/test_tools.py` — added imports + 8 test functions
- `src/agent_harness/tools/builtin/__init__.py` — new (empty)
- `src/agent_harness/tools/builtin/read_file.py` — new (ReadFileTool)
- `src/agent_harness/tools/builtin/write_file.py` — new (WriteFileTool)
- `src/agent_harness/tools/builtin/edit_file.py` — new (EditFileTool)
- `src/agent_harness/tools/builtin/run_shell.py` — new (RunShellTool)
- `src/agent_harness/tools/builtin/run_test.py` — new (RunTestTool)

## Concerns

- `test_run_test` passes only because `tests/test_import.py` exists and passes — it is a fragile coupling to another test file.
- `test_read_file_not_found` uses hardcoded `/nonexistent/file.txt` — platform-specific on Windows (works because path doesn't exist).
- RunShellTool uses `shell=True` — potential security concern in production but acceptable for dev harness.

## Report Path

`.superpowers/sdd/task-3.2-report.md`