# Task 1.2+1.3: LLMInterface + MockLLM

## Files Changed

| Action | File |
|--------|------|
| Created | `src/agent_harness/llm/__init__.py` |
| Created | `src/agent_harness/llm/interface.py` |
| Created | `src/agent_harness/llm/mock.py` |
| Created | `tests/test_llm.py` |

## TDD Evidence

### RED phase
```
ImportError while importing test module 'tests/test_llm.py'.
ModuleNotFoundError: No module named 'agent_harness.llm.interface'
```
→ 0 collected / 1 error (as expected — no interface module yet)

### GREEN phase
```
tests/test_llm.py::test_cannot_instantiate_abstract PASSED
tests/test_llm.py::test_mock_llm_returns_preset PASSED
tests/test_llm.py::test_mock_llm_consumes_queue PASSED
tests/test_llm.py::test_mock_llm_done_when_exhausted PASSED
```
→ 4 passed in 0.08s

## Commits

```
ad2f705 Task 1.2+1.3: LLMInterface + MockLLM
```

## Self-Review

- `LLMInterface` is an abstract base class with abstract `call()` method — instantiation correctly raises `TypeError`.
- `MockLLM` extends `LLMInterface`, uses a response queue with `call_count` tracking.
  - Returns presets in FIFO order (test: `test_mock_llm_returns_preset`, `test_mock_llm_consumes_queue`).
  - Falls back to empty `done` response when queue exhausted (test: `test_mock_llm_done_when_exhausted`).
- All 4 tests pass; no lint/style issues.