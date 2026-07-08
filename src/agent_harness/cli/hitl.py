from agent_harness.config.loader import load_config_with_profile
from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.resume import approve_and_execute, approve_execute_and_continue
from agent_harness.hitl.store import HITLStore
from agent_harness.runtime.factory import build_harness

DEFAULT_HITL_STORE_PATH = ".harness/hitl/requests.json"


def add_hitl_parser(subparsers):
    parser = subparsers.add_parser("hitl", help="manage human approval requests")
    hitl_subparsers = parser.add_subparsers(dest="hitl_command")

    list_parser = hitl_subparsers.add_parser("list", help="list HITL requests")
    list_parser.add_argument("--store", default=DEFAULT_HITL_STORE_PATH)
    list_parser.set_defaults(handler=_list)

    approve_parser = hitl_subparsers.add_parser("approve", help="approve and execute request")
    approve_parser.add_argument("request_id")
    approve_parser.add_argument("--config", default="config/agent-harness.yaml")
    approve_parser.add_argument("--profile", default=None)
    approve_parser.add_argument("--store", default=DEFAULT_HITL_STORE_PATH)
    approve_parser.add_argument("--continue", action="store_true", dest="continue_run")
    approve_parser.set_defaults(handler=_approve)

    deny_parser = hitl_subparsers.add_parser("deny", help="deny request")
    deny_parser.add_argument("request_id")
    deny_parser.add_argument("--store", default=DEFAULT_HITL_STORE_PATH)
    deny_parser.set_defaults(handler=_deny)


def _manager(store_path: str) -> HITLManager:
    return HITLManager(store=HITLStore(store_path))


def _list(args) -> int:
    requests = HITLStore(args.store).load()
    if not requests:
        print("No HITL requests found")
        return 0
    for request in requests:
        print(f"{request.id} {request.status} {request.action.tool} {request.reason}")
    return 0


def _approve(args) -> int:
    config = load_config_with_profile(args.config, args.profile)
    harness = build_harness(config, hitl_store_path=args.store)
    if args.continue_run:
        result = approve_execute_and_continue(harness, args.request_id)
        if result.halt_reason == "hitl_error" or result.halt_reason == "tool_error":
            print(result.answer)
            return 1
        print(result.answer)
        print(f"halt_reason={result.halt_reason} steps={result.steps}")
        return 0
    result = approve_and_execute(harness, args.request_id)
    if not result.success:
        print(result.error)
        return 1
    print(result.output)
    return 0


def _deny(args) -> int:
    manager = _manager(args.store)
    request = manager.deny(args.request_id)
    if request is None:
        print(f"HITL request not found: {args.request_id}")
        return 1
    print(f"{request.id} {request.status}")
    return 0
