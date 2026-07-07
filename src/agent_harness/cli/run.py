from agent_harness.agent.loop import agent_loop
from agent_harness.config.loader import load_config
from agent_harness.runtime.factory import build_harness
from agent_harness.runtime.result import RunResult


DEFAULT_TRACE_PATH = ".harness/runs/latest.jsonl"


def run_goal(goal: str, config_path: str | None = None, trace_path: str | None = None) -> RunResult:
    config = load_config(config_path or "config/agent-harness.yaml")
    run_trace_path = trace_path or DEFAULT_TRACE_PATH
    harness = build_harness(config, trace_path=run_trace_path)
    answer = agent_loop(goal, harness)
    return RunResult(
        answer=answer,
        halt_reason=harness.halt_reason,
        steps=harness.step,
        trace_path=run_trace_path,
    )


def add_run_parser(subparsers):
    parser = subparsers.add_parser("run", help="run a harness goal")
    parser.add_argument("goal")
    parser.add_argument("--config", default=None)
    parser.add_argument("--trace", default=None)
    parser.set_defaults(handler=_run)


def _run(args) -> int:
    result = run_goal(args.goal, args.config, args.trace)
    print(result.answer)
    print(f"halt_reason={result.halt_reason} steps={result.steps} trace={result.trace_path}")
    return 0
