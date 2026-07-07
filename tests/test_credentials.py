from agent_harness.credentials.manager import CredentialManager


class FakeBackend:
    def __init__(self):
        self.values = {}

    def get_password(self, service, username):
        return self.values.get((service, username))

    def set_password(self, service, username, password):
        self.values[(service, username)] = password

    def delete_password(self, service, username):
        self.values.pop((service, username), None)


def test_credentials_status_hides_secret():
    backend = FakeBackend()
    manager = CredentialManager(backend=backend)
    manager.update("sk-test-secret")

    status = manager.show_status()

    assert "configured" in status
    assert "sk-test-secret" not in status


def test_credentials_clear_removes_secret():
    backend = FakeBackend()
    manager = CredentialManager(backend=backend)
    manager.update("sk-test-secret")
    manager.clear()

    assert manager.get() is None
    assert manager.show_status() == "not configured"
