from agent_harness.agent.loop import agent_loop
from agent_harness.config.loader import load_config
from agent_harness.runtime.factory import build_harness
from agent_harness.runtime.result import RunResult


def run_goal(goal: str, config_path: str | None = None) -> RunResult:
    config = load_config(config_path or "config/agent-harness.yaml")
    harness = build_harness(config)
    answer = agent_loop(goal, harness)
    return RunResult(answer=answer, halt_reason=harness.halt_reason, steps=harness.step)


def add_run_parser(subparsers):
    parser = subparsers.add_parser("run", help="run a harness goal")
    parser.add_argument("goal")
    parser.add_argument("--config", default=None)
    parser.set_defaults(handler=_run)


def _run(args) -> int:
    result = run_goal(args.goal, args.config)
    print(result.answer)
    print(f"halt_reason={result.halt_reason} steps={result.steps}")
    return 0
