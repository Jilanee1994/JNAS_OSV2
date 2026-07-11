from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class BuildReport:
    goal: str
    plan: tuple[str, ...]
    status: str
    attempts: int


def create_plan(goal: str) -> tuple[str, ...]:
    return ("analyze goal", "generate project", "validate build report")


def run_build(goal: str, retry_limit: int = 1) -> BuildReport:
    plan = create_plan(goal)
    attempts = 1
    if not goal.strip() and retry_limit > 0:
        attempts += 1
        return BuildReport(goal, plan, "retry-required", attempts)
    return BuildReport(goal, plan, "success", attempts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUILD_AGENT orchestration CLI")
    parser.add_argument("--goal", default="Build a Python project")
    parser.add_argument("--retries", type=int, default=1)
    args = parser.parse_args(argv)
    report = run_build(args.goal, args.retries)
    print(f"Build agent report: {report.status}; plan: {', '.join(report.plan)}")
    return 0 if report.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
