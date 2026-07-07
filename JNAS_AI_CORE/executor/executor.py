"""Sequential execution engine for JNAS AI Core plans."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Callable

try:
    from JNAS_AI_CORE.memory import MemoryManager
    from JNAS_AI_CORE.orchestrator.interfaces import WorkerResult
    from JNAS_AI_CORE.orchestrator.router import RoutedTask
    from JNAS_AI_CORE.planner import ExecutionPlan, Task
except ImportError:
    from memory import MemoryManager
    from orchestrator.interfaces import WorkerResult
    from orchestrator.router import RoutedTask
    from planner import ExecutionPlan, Task

from .exceptions import ExecutionCancelled, ExecutionError
from .execution_context import ExecutionContext
from .execution_result import ExecutionResult
from .logger import get_executor_logger
from .pipeline import ExecutionPipeline
from .task_executor import TaskExecutor
from .validator import ExecutionValidator

ExecutionModeRunner = Callable[[ExecutionPlan], list[ExecutionResult]]


class Executor:
    """Execute planner-created execution plans."""

    def __init__(
        self,
        task_executor: TaskExecutor | None = None,
        memory_manager: MemoryManager | None = None,
        pipeline: ExecutionPipeline | None = None,
        validator: ExecutionValidator | None = None,
        execution_mode: str = "sequential",
        execution_modes: dict[str, ExecutionModeRunner] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.task_executor = task_executor or TaskExecutor()
        self.memory_manager = memory_manager or MemoryManager()
        self.pipeline = pipeline or ExecutionPipeline()
        self.validator = validator or ExecutionValidator()
        self.execution_mode = execution_mode
        self.execution_modes: dict[str, ExecutionModeRunner] = {
            "sequential": self._execute_sequential,
        }
        self.execution_modes.update(execution_modes or {})
        if self.execution_mode not in self.execution_modes:
            raise ValueError(f"Unsupported execution mode: {execution_mode}")
        self.logger = logger or get_executor_logger()
        self.context: ExecutionContext | None = None
        self.results: list[ExecutionResult] = []
        self.cancelled = False

    def execute_plan(self, plan: ExecutionPlan) -> list[ExecutionResult]:
        """Execute every task in an execution plan sequentially."""
        self.logger.info("Starting execution for plan %s.", plan.plan_id)
        self.validator.validate_plan(plan)
        self.context = ExecutionContext(plan_id=plan.plan_id)
        self.results = []
        self.cancelled = False
        results = self.execution_modes[self.execution_mode](plan)
        self.logger.info("Finished execution for plan %s.", plan.plan_id)
        return results

    def register_execution_mode(
        self,
        name: str,
        runner: ExecutionModeRunner,
    ) -> None:
        """Register a future execution mode such as parallel or distributed."""
        if not name:
            raise ValueError("Execution mode name must be a non-empty string.")
        self.execution_modes[name] = runner

    def _execute_sequential(self, plan: ExecutionPlan) -> list[ExecutionResult]:
        """Execute plan tasks one at a time in dependency order."""

        completed_task_ids: set[str] = set()
        for task in plan.tasks:
            if self.cancelled:
                raise ExecutionCancelled("Execution was cancelled.")
            self.validator.validate_dependencies(task, completed_task_ids)
            result = self.execute_task(task)
            self.results.append(result)
            self._save_result(result)
            if not result.success:
                break
            completed_task_ids.add(task.id)

        return list(self.results)

    def execute_task(self, task: Task) -> ExecutionResult:
        """Execute a single task through the execution pipeline."""
        if self.context is None:
            raise ExecutionError("Execution context has not been initialized.")

        self.context.current_task = task
        self.logger.info("Starting task %s: %s.", task.id, task.title)
        result = self.pipeline.run(task, self.context, self.task_executor.execute)
        if result.success:
            self.logger.info("Finished task %s in %.4fs.", task.id, result.duration)
        else:
            self.logger.error("Task %s failed in %.4fs: %s", task.id, result.duration, result.error)
        return result

    def cancel_execution(self) -> None:
        """Request cancellation before the next task starts."""
        self.cancelled = True
        self.logger.warning("Execution cancellation requested.")

    def resume_execution(self) -> None:
        """Clear cancellation state so a caller may execute a plan again."""
        self.cancelled = False
        self.logger.info("Execution resumed.")

    def get_status(self) -> dict[str, Any]:
        """Return current execution status."""
        return {
            "execution_id": self.context.execution_id if self.context else None,
            "plan_id": self.context.plan_id if self.context else None,
            "current_task": self.context.current_task.id if self.context and self.context.current_task else None,
            "results_count": len(self.results),
            "cancelled": self.cancelled,
            "execution_mode": self.execution_mode,
        }

    def _save_result(self, result: ExecutionResult) -> None:
        if self.context is None:
            return
        key = f"executor:{self.context.execution_id}:{result.task_id}"
        self.memory_manager.save_memory(key, asdict(result), tags=["executor", self.context.plan_id])


class ExecutorWorker:
    """Worker adapter for registering Executor with AIOrchestrator."""

    task_type = "executor"

    def __init__(self, executor: Executor | None = None) -> None:
        self.executor = executor or Executor()

    def execute(self, task: RoutedTask) -> WorkerResult:
        """Execute an `ExecutionPlan` supplied in routed task metadata."""
        plan = task.request.metadata.get("plan")
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionError("ExecutorWorker requires an ExecutionPlan in metadata['plan'].")
        results = self.executor.execute_plan(plan)
        return WorkerResult(
            success=all(result.success for result in results),
            message="Execution plan completed.",
            result=results,
        )
