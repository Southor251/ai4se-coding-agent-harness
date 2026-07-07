import argparse

from agent_harness.cli.credentials import add_credentials_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-harness")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="run a harness goal")
    subparsers.add_parser("demo", help="run deterministic mechanism demos")
    subparsers.add_parser("web", help="start the trace theater")
    add_credentials_parser(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.command == "credentials":
        return args.handler(args)
    if args.command in {"run", "demo", "web"}:
        print(f"{args.command} is not implemented yet")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

