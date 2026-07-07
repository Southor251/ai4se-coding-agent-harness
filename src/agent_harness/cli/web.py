def theater_command(trace_path: str | None = None) -> str:
    command = "streamlit run src/agent_harness/web/theater.py"
    if trace_path:
        return f"{command} # trace={trace_path}"
    return command


def add_web_parser(subparsers):
    parser = subparsers.add_parser("web", help="start the trace theater")
    parser.add_argument("--trace", default=None)
    parser.set_defaults(handler=_web)


def _web(args) -> int:
    print(theater_command(args.trace))
    return 0
