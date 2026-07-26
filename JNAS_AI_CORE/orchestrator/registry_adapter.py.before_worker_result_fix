"""Thin adapter between AIOrchestrator and ToolRegistry."""

from __future__ import annotations

from typing import Any

from .interfaces import BaseWorker, WorkerResult
from .router import RoutedTask

try:
    from JNAS_AI_CORE.registry import BaseTool, ToolMetadata, ToolRegistry
except ImportError:
    from registry import BaseTool, ToolMetadata, ToolRegistry


class WorkerToolAdapter:
    """Expose an orchestrator worker through the Tool Registry contract."""

    def __init__(self, worker: BaseWorker, metadata: ToolMetadata) -> None:
        self.worker = worker
        self.metadata = metadata

    def initialize(self) -> None:
        """Initialize the wrapped worker if it supports initialization."""
        initialize = getattr(self.worker, "initialize", None)
        if callable(initialize):
            initialize()

    def execute(self, payload: Any) -> WorkerResult:
        """Execute the wrapped worker."""
        return self.worker.execute(payload)

    def validate(self) -> bool:
        """Validate the wrapped worker has the required task contract."""
        return bool(getattr(self.worker, "task_type", ""))

    def shutdown(self) -> None:
        """Shutdown the wrapped worker if it supports shutdown."""
        shutdown = getattr(self.worker, "shutdown", None)
        if callable(shutdown):
            shutdown()


class RegistryWorkerAdapter:
    """Expose a registry tool as an orchestrator worker."""

    def __init__(self, tool: BaseTool, task_type: str) -> None:
        self.tool = tool
        self.task_type = task_type

    def execute(self, task: RoutedTask) -> WorkerResult:
        """Execute a registry tool for a routed task."""
        result = self.tool.execute(task)
        if isinstance(result, WorkerResult):
            return result
        return WorkerResult(
            success=True,
            message="Registry tool executed.",
            result=result,
        )


class RegistryAdapter:
    """Resolve orchestrator workers from ToolRegistry metadata."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def register_worker(
        self,
        worker: BaseWorker,
        metadata: ToolMetadata,
    ) -> None:
        """Register an orchestrator worker as a registry tool."""
        self.registry.register_tool(WorkerToolAdapter(worker, metadata))

    def resolve_worker(self, task_type: str) -> BaseWorker | None:
        """Return the highest-priority registry worker for a task type."""
        matches = self.registry.find_tools_by_task(task_type)
        if not matches:
            return None
        return RegistryWorkerAdapter(matches[0].tool, task_type)
