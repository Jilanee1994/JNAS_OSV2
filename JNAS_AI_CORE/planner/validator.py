"""Validation rules for execution plans."""

from __future__ import annotations

from .exceptions import PlanValidationError
from .plan import ExecutionPlan
from .task import Task


class PlanValidator:
    """Validate structural correctness of execution plans."""

    def validate(self, plan: ExecutionPlan) -> bool:
        """Validate all supported plan rules."""
        self._validate_required_fields(plan)
        self._validate_duplicate_task_ids(plan.tasks)
        self._validate_dependencies_exist(plan.tasks)
        self._validate_task_ordering(plan.tasks)
        self._validate_no_circular_dependencies(plan.tasks)
        return True

    def _validate_required_fields(self, plan: ExecutionPlan) -> None:
        if not plan.plan_id:
            raise PlanValidationError("ExecutionPlan.plan_id is required.")
        if not plan.goal or not plan.goal.strip():
            raise PlanValidationError("ExecutionPlan.goal is required.")
        if not plan.tasks:
            raise PlanValidationError("ExecutionPlan.tasks must not be empty.")
        for task in plan.tasks:
            if not task.id:
                raise PlanValidationError("Task.id is required.")
            if not task.title:
                raise PlanValidationError(f"Task.title is required for {task.id}.")
            if not task.description:
                raise PlanValidationError(f"Task.description is required for {task.id}.")

    def _validate_duplicate_task_ids(self, tasks: list[Task]) -> None:
        seen = set()
        for task in tasks:
            if task.id in seen:
                raise PlanValidationError(f"Duplicate task id: {task.id}")
            seen.add(task.id)

    def _validate_dependencies_exist(self, tasks: list[Task]) -> None:
        task_ids = {task.id for task in tasks}
        for task in tasks:
            for dependency in task.dependencies:
                if dependency not in task_ids:
                    raise PlanValidationError(
                        f"Task {task.id} depends on missing task {dependency}."
                    )

    def _validate_task_ordering(self, tasks: list[Task]) -> None:
        position = {task.id: index for index, task in enumerate(tasks)}
        for task in tasks:
            for dependency in task.dependencies:
                if position[dependency] >= position[task.id]:
                    raise PlanValidationError(
                        f"Task {task.id} appears before dependency {dependency}."
                    )

    def _validate_no_circular_dependencies(self, tasks: list[Task]) -> None:
        graph = {task.id: list(task.dependencies) for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise PlanValidationError(f"Circular dependency detected at {task_id}.")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in graph[task_id]:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)
