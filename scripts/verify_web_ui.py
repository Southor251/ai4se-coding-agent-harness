import argparse
import sys
import urllib.error
import urllib.request


def validate_body(body: str, expected_text: str | None = "Agent Harness Console") -> bool:
    if expected_text and expected_text in body:
        return True
    lowered = body.lower()
    return "streamlit" in lowered and ("static" in lowered or "script" in lowered)


def verify_url(url: str, expected_text: str | None = "Agent Harness Console", timeout: float = 10.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status = response.getcode()
            body = response.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as exc:
        return False, f"request failed: {exc}"
    if status != 200:
        return False, f"unexpected status: {status}"
    if not validate_body(body, expected_text):
        return False, "response did not look like the Agent Harness Web UI"
    return True, f"ok status={status} url={url}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the running Agent Harness Web UI.")
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--expect-text", default="Agent Harness Console")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    expected = args.expect_text or None
    ok, message = verify_url(args.url, expected_text=expected, timeout=args.timeout)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
