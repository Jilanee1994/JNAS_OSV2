"""Task execution adapters."""

from __future__ import annotations

import time
from typing import Any, Protocol

try:
    from JNAS_AI_CORE.planner import Task
except ImportError:
    from planner import Task

from .execution_context import ExecutionContext
from .execution_result import ExecutionResult


class TaskWorker(Protocol):
    """Protocol for executable task workers."""

    name: str

    def execute(self, task: Task, context: ExecutionContext) -> Any:
        """Execute a task and return worker-specific output."""


class GenericTaskWorker:
    """Default worker for deterministic task acknowledgement."""

    name = "generic"

    def execute(self, task: Task, context: ExecutionContext) -> dict[str, Any]:
        """Return a structured acknowledgement for a planned task."""
        return {
            "execution_id": context.execution_id,
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": "completed",
        }


class TaskExecutor:
    """Executes individual tasks through registered workers."""

    def __init__(self, workers: dict[str, TaskWorker] | None = None) -> None:
        self.workers: dict[str, TaskWorker] = {"generic": GenericTaskWorker()}
        for worker in (workers or {}).values():
            self.register_worker(worker)

    def register_worker(self, worker: TaskWorker) -> None:
        """Register or replace a task worker."""
        self.workers[worker.name] = worker

    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        """Execute one task and return an execution result."""
        started = time.perf_counter()
        worker = self._select_worker(task)
        try:
            output = worker.execute(task, context)
            return ExecutionResult(
                task_id=task.id,
                success=True,
                output=output,
                duration=time.perf_counter() - started,
                metadata={"worker": worker.name},
            )
        except Exception as exc:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                error=str(exc),
                duration=time.perf_counter() - started,
                metadata={"worker": worker.name},
            )

    def _select_worker(self, task: Task) -> TaskWorker:
        worker_name = str(task.metadata.get("worker", "generic"))
        return self.workers.get(worker_name, self.workers["generic"])
