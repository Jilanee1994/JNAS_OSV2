"""Validation for execution readiness."""

from __future__ import annotations

try:
    from JNAS_AI_CORE.planner import ExecutionPlan, Task
except ImportError:
    from planner import ExecutionPlan, Task

from .exceptions import ExecutionValidationError


class ExecutionValidator:
    """Validate execution order and dependency state."""

    def validate_plan(self, plan: ExecutionPlan) -> bool:
        """Validate that the plan can be executed sequentially."""
        if not plan.tasks:
            raise ExecutionValidationError("Execution plan has no tasks.")

        seen: set[str] = set()
        for task in plan.tasks:
            self.validate_task(task)
            missing = [dependency for dependency in task.dependencies if dependency not in seen]
            if missing:
                raise ExecutionValidationError(
                    f"Task {task.id} has unsatisfied dependencies: {', '.join(missing)}"
                )
            seen.add(task.id)
        return True

    def validate_task(self, task: Task) -> bool:
        """Validate a single task exists and has required execution fields."""
        if task is None:
            raise ExecutionValidationError("Task is required.")
        if not task.id:
            raise ExecutionValidationError("Task.id is required.")
        if not task.title:
            raise ExecutionValidationError(f"Task.title is required for {task.id}.")
        return True

    def validate_dependencies(
        self,
        task: Task,
        completed_task_ids: set[str],
    ) -> bool:
        """Validate a task's dependencies are completed."""
        missing = [
            dependency
            for dependency in task.dependencies
            if dependency not in completed_task_ids
        ]
        if missing:
            raise ExecutionValidationError(
                f"Task {task.id} dependencies are not complete: {', '.join(missing)}"
            )
        return True
