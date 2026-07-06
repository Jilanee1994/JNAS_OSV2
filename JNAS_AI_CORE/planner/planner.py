"""AI planning engine for JNAS AI Core."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any, Literal

from .plan import ExecutionPlan
from .strategy import StrategyEngine
from .task import Task
from .validator import PlanValidator

try:
    from JNAS_AI_CORE.orchestrator.interfaces import WorkerResult
    from JNAS_AI_CORE.orchestrator.router import RoutedTask
except ImportError:
    WorkerResult = None
    RoutedTask = Any

ExportFormat = Literal["json", "markdown"]


class Planner:
    """Create, validate, optimize, and export execution plans."""

    def __init__(
        self,
        strategy_engine: StrategyEngine | None = None,
        validator: PlanValidator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.strategy_engine = strategy_engine or StrategyEngine()
        self.validator = validator or PlanValidator()
        self.logger = logger or logging.getLogger(__name__)

    def create_plan(
        self,
        goal: str,
        strategy_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionPlan:
        """Convert a user goal into a structured execution plan."""
        if not goal or not goal.strip():
            raise ValueError("Goal must be a non-empty string.")

        self.logger.info("Creating execution plan.")
        strategy = self.strategy_engine.select_strategy(goal, strategy_name)
        self.logger.info("Selected planning strategy: %s.", strategy.name)
        tasks = strategy.create_tasks(goal)
        plan = ExecutionPlan(
            goal=goal,
            tasks=tasks,
            metadata={"strategy": strategy.name, **(metadata or {})},
        )
        self.validate_plan(plan)
        return plan

    def validate_plan(self, plan: ExecutionPlan) -> bool:
        """Validate a plan and return true when valid."""
        self.logger.info("Validating execution plan %s.", plan.plan_id)
        return self.validator.validate(plan)

    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Return a plan with tasks ordered by dependency and priority."""
        self.logger.info("Optimizing execution plan %s.", plan.plan_id)
        self.validator._validate_required_fields(plan)
        self.validator._validate_duplicate_task_ids(plan.tasks)
        self.validator._validate_dependencies_exist(plan.tasks)
        self.validator._validate_no_circular_dependencies(plan.tasks)
        plan.tasks = self._sort_tasks_by_dependencies(plan.tasks)
        self.validate_plan(plan)
        return plan

    def export_plan(
        self,
        plan: ExecutionPlan,
        export_format: ExportFormat = "json",
    ) -> str:
        """Export a plan as JSON or Markdown."""
        self.logger.info("Exporting execution plan %s as %s.", plan.plan_id, export_format)
        self.validate_plan(plan)
        if export_format == "json":
            return self._export_json(plan)
        if export_format == "markdown":
            return self._export_markdown(plan)
        raise ValueError(f"Unsupported export format: {export_format}")

    def _export_json(self, plan: ExecutionPlan) -> str:
        return json.dumps(
            self._plan_to_dict(plan),
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

    def _export_markdown(self, plan: ExecutionPlan) -> str:
        lines = [
            f"# Execution Plan: {plan.goal}",
            "",
            f"- Plan ID: `{plan.plan_id}`",
            f"- Created At: `{plan.created_at.isoformat()}`",
            f"- Strategy: `{plan.metadata.get('strategy', 'unknown')}`",
            "",
            "## Tasks",
            "",
        ]
        for index, task in enumerate(plan.tasks, start=1):
            dependencies = ", ".join(task.dependencies) if task.dependencies else "none"
            lines.extend(
                [
                    f"### Task {index}: {task.title}",
                    "",
                    f"- ID: `{task.id}`",
                    f"- Description: {task.description}",
                    f"- Priority: {task.priority}",
                    f"- Status: `{task.status}`",
                    f"- Dependencies: {dependencies}",
                    f"- Estimated Duration: {task.estimated_duration}",
                    "",
                ]
            )
        return "\n".join(lines).strip() + "\n"

    def _plan_to_dict(self, plan: ExecutionPlan) -> dict[str, Any]:
        data = asdict(plan)
        data["created_at"] = self._format_datetime(plan.created_at)
        return data

    def _format_datetime(self, value: datetime) -> str:
        return value.isoformat()

    def _sort_tasks_by_dependencies(self, tasks: list[Task]) -> list[Task]:
        remaining = {task.id: task for task in tasks}
        ordered: list[Task] = []
        completed: set[str] = set()

        while remaining:
            ready = [
                task
                for task in remaining.values()
                if all(dependency in completed for dependency in task.dependencies)
            ]
            if not ready:
                break
            ready.sort(key=lambda task: (task.priority, task.id))
            for task in ready:
                ordered.append(task)
                completed.add(task.id)
                remaining.pop(task.id)

        return ordered + sorted(remaining.values(), key=lambda task: (task.priority, task.id))


class PlannerWorker:
    """Worker adapter for registering Planner with AIOrchestrator."""

    task_type = "planner"

    def __init__(self, planner: Planner | None = None) -> None:
        self.planner = planner or Planner()

    def execute(self, task: RoutedTask) -> Any:
        """Create an execution plan for a routed planner task."""
        plan = self.planner.create_plan(task.request.user_input)
        if WorkerResult is None:
            return plan
        return WorkerResult(
            success=True,
            message="Execution plan created.",
            result=plan,
        )
