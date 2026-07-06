"""Tests for the orchestrator registry adapter."""

from __future__ import annotations

from JNAS_AI_CORE.orchestrator import RegistryAdapter, RoutedTask, UserRequest, WorkerResult
from JNAS_AI_CORE.registry import ToolMetadata, ToolRegistry


class FakeWorker:
    task_type = "code_generation"

    def execute(self, task: RoutedTask) -> WorkerResult:
        return WorkerResult(
            success=True,
            message="fake worker executed",
            result=task.request.user_input,
        )


def test_registry_adapter_resolves_worker_by_supported_task() -> None:
    registry = ToolRegistry()
    adapter = RegistryAdapter(registry)
    adapter.register_worker(
        FakeWorker(),
        ToolMetadata(
            tool_id="core.code_agent",
            name="CodeAgent",
            description="Code generation worker.",
            version="1.0.0",
            author="JNAS",
            category="code",
            supported_tasks=["code_generation"],
            input_types=["RoutedTask"],
            output_types=["WorkerResult"],
            priority=1,
        ),
    )

    worker = adapter.resolve_worker("code_generation")
    result = worker.execute(RoutedTask("code_generation", UserRequest("make code")))

    assert result.success is True
    assert result.result == "make code"
