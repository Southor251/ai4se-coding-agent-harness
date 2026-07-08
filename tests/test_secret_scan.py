from scripts.secret_scan import scan_text


def test_secret_scan_allows_benign_key_documentation():
    findings = scan_text("README.md", "API key is stored in the credential manager.")

    assert findings == []


def test_secret_scan_flags_private_key_material():
    findings = scan_text("secret.txt", "-----BEGIN PRIVATE KEY-----")

    assert findings
    assert findings[0].kind == "private_key"


def test_secret_scan_flags_todo_markers():
    findings = scan_text("src/example.py", "# TODO: finish this")

    assert findings
    assert findings[0].kind == "todo_marker"
