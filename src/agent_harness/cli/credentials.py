from agent_harness.credentials.manager import CredentialManager


def add_credentials_parser(subparsers):
    parser = subparsers.add_parser("credentials", help="manage API credentials")
    credential_subparsers = parser.add_subparsers(dest="credential_command")

    show = credential_subparsers.add_parser("show", help="show credential status")
    show.set_defaults(handler=_show)

    update = credential_subparsers.add_parser("update", help="update credential")
    update.add_argument("secret")
    update.set_defaults(handler=_update)

    clear = credential_subparsers.add_parser("clear", help="clear credential")
    clear.set_defaults(handler=_clear)


def _show(args) -> int:
    print(CredentialManager().show_status())
    return 0


def _update(args) -> int:
    CredentialManager().update(args.secret)
    print("configured")
    return 0


def _clear(args) -> int:
    CredentialManager().clear()
    print("not configured")
    return 0

