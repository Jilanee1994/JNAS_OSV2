"""Execution pipeline stages."""

from __future__ import annotations

from typing import Callable

try:
    from JNAS_AI_CORE.planner import Task
except ImportError:
    from planner import Task

from .execution_context import ExecutionContext
from .execution_result import ExecutionResult

BeforeTaskHook = Callable[[Task, ExecutionContext], None]
ExecuteHook = Callable[[Task, ExecutionContext], ExecutionResult]
AfterTaskHook = Callable[[Task, ExecutionContext, ExecutionResult], None]
ErrorHandler = Callable[[Task, ExecutionContext, ExecutionResult], None]


class ExecutionPipeline:
    """Pipeline for before, execute, after, and error stages."""

    def __init__(self) -> None:
        self.before_task_hooks: list[BeforeTaskHook] = []
        self.after_task_hooks: list[AfterTaskHook] = []
        self.error_handlers: list[ErrorHandler] = []

    def add_before_task(self, hook: BeforeTaskHook) -> None:
        """Add a before-task hook."""
        self.before_task_hooks.append(hook)

    def add_after_task(self, hook: AfterTaskHook) -> None:
        """Add an after-task hook."""
        self.after_task_hooks.append(hook)

    def add_error_handler(self, handler: ErrorHandler) -> None:
        """Add an error handler."""
        self.error_handlers.append(handler)

    def run(
        self,
        task: Task,
        context: ExecutionContext,
        execute: ExecuteHook,
    ) -> ExecutionResult:
        """Run all pipeline stages for one task."""
        for hook in self.before_task_hooks:
            hook(task, context)

        result = execute(task, context)

        if result.success:
            for hook in self.after_task_hooks:
                hook(task, context, result)
        else:
            for handler in self.error_handlers:
                handler(task, context, result)

        return result
