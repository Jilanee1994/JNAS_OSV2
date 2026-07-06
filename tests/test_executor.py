"""Tests for the JNAS AI Core executor."""

from __future__ import annotations

import pytest

from JNAS_AI_CORE.executor import (
    ExecutionContext,
    ExecutionPipeline,
    ExecutionValidationError,
    Executor,
    TaskExecutor,
)
from JNAS_AI_CORE.memory import MemoryManager
from JNAS_AI_CORE.planner import ExecutionPlan, Task


def make_plan() -> ExecutionPlan:
    return ExecutionPlan(
        goal="Execute test plan",
        tasks=[
            Task("task-1", "First", "First task"),
            Task("task-2", "Second", "Second task", dependencies=["task-1"]),
        ],
    )


def make_executor(tmp_path) -> Executor:
    return Executor(memory_manager=MemoryManager(storage_dir=tmp_path))


def test_sequential_execution(tmp_path) -> None:
    executor = make_executor(tmp_path)

    results = executor.execute_plan(make_plan())

    assert [result.task_id for result in results] == ["task-1", "task-2"]
    assert all(result.success for result in results)


def test_dependency_validation(tmp_path) -> None:
    executor = make_executor(tmp_path)
    plan = ExecutionPlan(
        goal="Invalid order",
        tasks=[
            Task("task-2", "Second", "Second task", dependencies=["task-1"]),
            Task("task-1", "First", "First task"),
        ],
    )

    with pytest.raises(ExecutionValidationError):
        executor.execute_plan(plan)


def test_execution_context(tmp_path) -> None:
    executor = make_executor(tmp_path)

    executor.execute_plan(make_plan())
    status = executor.get_status()

    assert status["plan_id"] == executor.context.plan_id
    assert status["current_task"] == "task-2"
    assert status["execution_mode"] == "sequential"


def test_result_collection(tmp_path) -> None:
    executor = make_executor(tmp_path)

    results = executor.execute_plan(make_plan())

    assert executor.results == results
    assert len(executor.results) == 2
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_pipeline_execution(tmp_path) -> None:
    events: list[str] = []
    pipeline = ExecutionPipeline()
    pipeline.add_before_task(lambda task, context: events.append(f"before:{task.id}"))
    pipeline.add_after_task(
        lambda task, context, result: events.append(f"after:{task.id}")
    )
    executor = Executor(
        memory_manager=MemoryManager(storage_dir=tmp_path),
        pipeline=pipeline,
    )

    executor.execute_plan(make_plan())

    assert events == ["before:task-1", "after:task-1", "before:task-2", "after:task-2"]


def test_failure_handling(tmp_path) -> None:
    class FailingWorker:
        name = "failing"

        def execute(self, task: Task, context: ExecutionContext) -> str:
            raise RuntimeError("worker failed")

    task_executor = TaskExecutor()
    task_executor.register_worker(FailingWorker())
    plan = ExecutionPlan(
        goal="Failure plan",
        tasks=[
            Task("task-1", "Fails", "Failure task", metadata={"worker": "failing"}),
            Task("task-2", "Skipped", "Should not run", dependencies=["task-1"]),
        ],
    )
    executor = Executor(
        task_executor=task_executor,
        memory_manager=MemoryManager(storage_dir=tmp_path),
    )

    results = executor.execute_plan(plan)

    assert len(results) == 1
    assert results[0].success is False
    assert results[0].error == "worker failed"


def test_resume_execution(tmp_path) -> None:
    executor = make_executor(tmp_path)

    executor.cancel_execution()
    executor.resume_execution()

    assert executor.get_status()["cancelled"] is False
