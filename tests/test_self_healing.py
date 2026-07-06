"""Tests for the autonomous self-healing engine."""

from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.executor import ExecutionResult
from JNAS_AI_CORE.memory import MemoryManager
from JNAS_AI_CORE.self_healing import (
    FailureAnalyzer,
    RecoveryPatch,
    RecoveryPolicy,
    RetryPolicy,
    SelfHealingEngine,
)


class PatchGenerator:
    def __init__(self, content: str) -> None:
        self.content = content

    def generate_patch(self, payload):
        return {
            "path": payload["source_path"],
            "content": self.content,
            "summary": "fixed syntax",
        }


def test_retry(tmp_path: Path) -> None:
    engine = SelfHealingEngine(
        memory_manager=MemoryManager(storage_dir=tmp_path / "memory"),
        retry_policy=RetryPolicy(max_retries=1),
    )

    result = engine.recover(
        ExecutionResult("task-1", success=False, error="RuntimeError: temporary"),
    )

    assert result.success is True
    assert result.strategy == RecoveryPolicy.RETRY
    assert result.retry_count == 1


def test_patch(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("value =", encoding="utf-8")
    engine = SelfHealingEngine(
        memory_manager=MemoryManager(storage_dir=tmp_path / "memory"),
        patch_generator=PatchGenerator("value = 1\n"),
    )

    result = engine.recover(
        ExecutionResult("task-2", success=False, error="SyntaxError"),
        traceback_text="SyntaxError: invalid syntax",
        source_path=source,
        validation_target=source,
    )

    assert result.success is True
    assert source.read_text(encoding="utf-8") == "value = 1\n"


def test_rollback(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("value = 1\n", encoding="utf-8")
    engine = SelfHealingEngine(
        memory_manager=MemoryManager(storage_dir=tmp_path / "memory"),
        patch_generator=PatchGenerator("value =\n"),
    )

    result = engine.recover(
        ExecutionResult("task-3", success=False, error="SyntaxError"),
        source_path=source,
        validation_target=source,
    )

    assert result.success is False
    assert source.read_text(encoding="utf-8") == "value = 1\n"


def test_recovery_history(tmp_path: Path) -> None:
    engine = SelfHealingEngine(
        memory_manager=MemoryManager(storage_dir=tmp_path / "memory"),
        retry_policy=RetryPolicy(max_retries=1),
    )

    engine.recover(ExecutionResult("task-4", success=False, error="RuntimeError"))

    assert engine.history.last() is not None
    assert engine.history.last().recovery_action == RecoveryPolicy.RETRY


def test_failure_classification() -> None:
    analyzer = FailureAnalyzer()

    analysis = analyzer.analyze(
        ExecutionResult("task-5", success=False, error="ModuleNotFoundError"),
    )

    assert analysis.category == "Import Error"


def test_policy_selection() -> None:
    policy = RecoveryPolicy()
    analysis = FailureAnalyzer().analyze(
        ExecutionResult("task-6", success=False, error="SyntaxError"),
    )

    assert policy.select_strategy(analysis) == RecoveryPolicy.PATCH


def test_memory_storage(tmp_path: Path) -> None:
    memory = MemoryManager(storage_dir=tmp_path / "memory")
    engine = SelfHealingEngine(
        memory_manager=memory,
        retry_policy=RetryPolicy(max_retries=1),
    )

    engine.recover(ExecutionResult("task-7", success=False, error="RuntimeError"))

    assert memory.search_memory("task-7")


def test_patch_object_generation(tmp_path: Path) -> None:
    class ObjectPatchGenerator:
        def generate_patch(self, payload):
            return RecoveryPatch(Path(payload["source_path"]), "ok = True\n", "object patch")

    source = tmp_path / "fixed.py"
    engine = SelfHealingEngine(
        memory_manager=MemoryManager(storage_dir=tmp_path / "memory"),
        patch_generator=ObjectPatchGenerator(),
    )

    result = engine.recover(
        ExecutionResult("task-8", success=False, error="SyntaxError"),
        source_path=source,
        validation_target=source,
    )

    assert result.success is True
    assert source.read_text(encoding="utf-8") == "ok = True\n"
