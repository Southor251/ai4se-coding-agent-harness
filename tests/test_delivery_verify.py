from scripts.verify_delivery import build_checks


def test_delivery_verify_builds_expected_checks():
    checks = build_checks()
    names = [check.name for check in checks]

    assert names == [
        "pytest",
        "ruff",
        "cli_run",
        "hitl_list",
        "secret_scan",
    ]
    assert checks[0].command[1:3] == ["-m", "pytest"]
    assert checks[2].command[1:3] == ["-m", "agent_harness.cli.main"]
    assert "--profile" not in checks[2].command
