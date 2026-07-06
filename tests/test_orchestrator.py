"""Tests for the JNAS AI Core orchestrator."""

from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.orchestrator import AIOrchestrator, TaskRouter, WorkerResult
from JNAS_AI_CORE.orchestrator.router import RoutedTask


class FakeCodeAgent:
    def generate_code(self, task: str) -> str:
        return f"generated:{task}"


class FakeLLMManager:
    def generate(self, prompt: str) -> str:
        return f"chat:{prompt}"


class FakeBuilderEngine:
    def __init__(self) -> None:
        self.built_modules: list[str] = []

    def build(self, module_name: str) -> dict[str, str]:
        self.built_modules.append(module_name)
        return {"module_name": module_name}


def make_orchestrator() -> AIOrchestrator:
    return AIOrchestrator(
        code_agent=FakeCodeAgent(),
        llm_manager=FakeLLMManager(),
        builder_engine=FakeBuilderEngine(),
        project_root=Path("."),
    )


def test_initialization() -> None:
    orchestrator = make_orchestrator()

    orchestrator.initialize()

    assert orchestrator.initialized is True


def test_request_routing_for_builder() -> None:
    orchestrator = make_orchestrator()

    routed_task = orchestrator.route_task("builder planner")

    assert routed_task.task_type == TaskRouter.BUILDER
    assert routed_task.payload["module_name"] == "planner"


def test_unknown_task_handling() -> None:
    orchestrator = make_orchestrator()
    orchestrator.initialize()
    routed_task = orchestrator.route_task("ok")

    response = orchestrator.execute(routed_task)

    assert response.success is False
    assert response.message == "Unknown task type."
    assert response.errors


def test_execution_response_for_chat() -> None:
    orchestrator = make_orchestrator()

    response = orchestrator.handle_request("What is JNAS?")

    assert response.success is True
    assert response.message == "Chat response generated."
    assert response.result == "chat:What is JNAS?"
    assert response.execution_time >= 0
    assert response.errors == []


def test_execution_response_for_code_generation() -> None:
    orchestrator = make_orchestrator()

    response = orchestrator.handle_request("generate code for a calculator")

    assert response.success is True
    assert response.message == "Code generation completed."
    assert response.result == "generated:generate code for a calculator"


def test_custom_worker_registration() -> None:
    class MemoryWorker:
        task_type = "memory"

        def execute(self, task: RoutedTask) -> WorkerResult:
            return WorkerResult(
                success=True,
                message="Memory task completed.",
                result=task.request.user_input,
            )

    orchestrator = make_orchestrator()
    orchestrator.initialize()
    orchestrator.register_worker(MemoryWorker())
    request = orchestrator.route_task(
        "remember this",
    )
    request = RoutedTask(
        task_type="memory",
        request=request.request,
    )

    response = orchestrator.execute(request)

    assert response.success is True
    assert response.message == "Memory task completed."
    assert response.result == "remember this"
