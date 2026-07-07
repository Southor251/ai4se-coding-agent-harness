import argparse

from agent_harness.cli.credentials import add_credentials_parser
from agent_harness.cli.demo import add_demo_parser
from agent_harness.cli.run import add_run_parser
from agent_harness.cli.web import add_web_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-harness")
    subparsers = parser.add_subparsers(dest="command")

    add_run_parser(subparsers)
    add_demo_parser(subparsers)
    add_web_parser(subparsers)
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
    if hasattr(args, "handler"):
        return args.handler(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
