# Task 0.3: Configure CI

**Files:**
- Create: `.gitlab-ci.yml`
- Create: `.github/workflows/test.yml`

**Goal:** Set up CI with GitHub Actions (push runs tests) and GitLab CI (unit-test job).

**Dependencies:** T0.1 (pyproject.toml, Makefile exist)

**Verification:** CI triggers pass after push

## Implementation Details

### .github/workflows/test.yml

```yaml
name: tests
on: [push]
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e .
      - run: pip install ruff
      - run: make test
      - run: make lint
```

### .gitlab-ci.yml

```yaml
unit-test:
  script:
    - pip install -e .
    - pip install ruff
    - make test
    - make lint
  tags:
    - python
```

## TDD Steps

1. Create both CI files
2. Commit and push
3. Verify GitHub Actions triggers on push