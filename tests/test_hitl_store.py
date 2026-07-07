from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.store import HITLStore
from agent_harness.models import AgentAction


def test_create_request_persists_to_store(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))

    request = manager.create_request(
        AgentAction(type="call_tool", tool="write_file", args={"path": "note.txt"}),
        "review required",
    )

    assert store_path.exists()
    reloaded = HITLStore(store_path).load()
    assert len(reloaded) == 1
    assert reloaded[0].id == request.id
    assert reloaded[0].action.tool == "write_file"
    assert reloaded[0].reason == "review required"
    assert reloaded[0].status == "pending"


def test_manager_loads_existing_requests_from_store(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.create_request(AgentAction(type="call_tool", tool="read_file"), "review")

    reloaded = HITLManager(store=HITLStore(store_path))

    assert reloaded.find(request.id) is not None
    assert reloaded.find(request.id).status == "pending"


def test_approve_and_deny_are_persisted(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    approved = manager.create_request(AgentAction(type="call_tool", tool="read_file"), "review")
    denied = manager.create_request(AgentAction(type="call_tool", tool="write_file"), "review")

    manager.approve(approved.id)
    manager.deny(denied.id)

    reloaded = HITLManager(store=HITLStore(store_path))
    assert reloaded.find(approved.id).status == "approved"
    assert reloaded.find(approved.id).decided_by == "human"
    assert reloaded.find(denied.id).status == "denied"
    assert reloaded.find(denied.id).decided_by == "human"


def test_hitl_manager_without_store_remains_in_memory():
    manager = HITLManager()
    request = manager.create_request(AgentAction(type="call_tool", tool="read_file"), "review")

    assert manager.find(request.id) is request
