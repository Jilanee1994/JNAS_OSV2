"""Autonomous recovery engine for failed executions."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.executor import ExecutionResult
    from JNAS_AI_CORE.memory import MemoryManager
    from JNAS_AI_CORE.orchestrator.interfaces import WorkerResult
    from JNAS_AI_CORE.orchestrator.registry_adapter import RegistryAdapter
except ImportError:
    from executor import ExecutionResult
    from memory import MemoryManager
    from orchestrator.interfaces import WorkerResult
    from orchestrator.registry_adapter import RegistryAdapter

from .analyzer import FailureAnalyzer, FailureAnalysis
from .exceptions import HealingError
from .history import RecoveryHistory, RecoveryHistoryEntry
from .logger import get_self_healing_logger
from .patcher import CodePatcher, RecoveryPatch
from .policy import RecoveryPolicy
from .recovery import RecoveryResult
from .retry import RetryPolicy


class SelfHealingEngine:
    """Recover from failed executor results without replacing Executor."""

    def __init__(
        self,
        analyzer: FailureAnalyzer | None = None,
        policy: RecoveryPolicy | None = None,
        retry_policy: RetryPolicy | None = None,
        patcher: CodePatcher | None = None,
        memory_manager: MemoryManager | None = None,
        registry_adapter: RegistryAdapter | None = None,
        patch_generator: Any | None = None,
        history: RecoveryHistory | None = None,
    ) -> None:
        self.analyzer = analyzer or FailureAnalyzer()
        self.policy = policy or RecoveryPolicy()
        self.retry_policy = retry_policy or RetryPolicy()
        self.patcher = patcher or CodePatcher()
        self.memory_manager = memory_manager or MemoryManager()
        self.registry_adapter = registry_adapter
        self.patch_generator = patch_generator
        self.history = history or RecoveryHistory()
        self.logger = get_self_healing_logger()

    def recover(
        self,
        failure: ExecutionResult,
        traceback_text: str = "",
        source_path: Path | None = None,
        validation_target: Path | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RecoveryResult:
        """Recover from a failed execution result."""
        started = time.perf_counter()
        analysis = self.analyzer.analyze(failure, traceback_text, metadata)
        strategy = self.policy.select_strategy(analysis)
        self.logger.info("Recovery strategy selected: %s.", strategy)

        if strategy == RecoveryPolicy.RETRY:
            return self._retry_recovery(analysis, started)
        if strategy == RecoveryPolicy.PATCH:
            return self._patch_recovery(analysis, started, source_path, validation_target)
        if strategy == RecoveryPolicy.ROLLBACK:
            return self._finish(False, "Rollback required.", analysis, strategy, started)
        if strategy == RecoveryPolicy.SKIP:
            return self._finish(True, "Failure skipped by policy.", analysis, strategy, started)
        if strategy == RecoveryPolicy.ABORT:
            return self._finish(False, "Recovery aborted by policy.", analysis, strategy, started)
        return self._finish(False, "Recovery escalated.", analysis, strategy, started)

    def generate_patch(
        self,
        analysis: FailureAnalysis,
        source_path: Path | None,
    ) -> RecoveryPatch:
        """Generate a patch through ToolRegistry or an injected patch generator."""
        payload = {"analysis": asdict(analysis), "source_path": str(source_path or "")}
        generated = self._generate_with_registry(analysis, payload)
        if generated is None and self.patch_generator is not None:
            generated = self.patch_generator.generate_patch(payload)
        return self._coerce_patch(generated, source_path)

    def validate_recovery(self, validation_target: Path | None = None) -> tuple[bool, str]:
        """Run validation after patching."""
        command = [sys.executable, "-m", "compileall", str(validation_target)] if validation_target else [
            sys.executable,
            "-m",
            "compileall",
            "JNAS_AI_CORE",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode == 0, (result.stdout or "") + (result.stderr or "")

    def _retry_recovery(self, analysis: FailureAnalysis, started: float) -> RecoveryResult:
        retry_count = 0
        while self.retry_policy.can_retry(retry_count):
            delay = self.retry_policy.delay_for(retry_count)
            if delay:
                time.sleep(delay)
            retry_count += 1
            return self._finish(
                True,
                "Retry scheduled by recovery policy.",
                analysis,
                RecoveryPolicy.RETRY,
                started,
                retry_count=retry_count,
            )
        return self._finish(False, "Retry limit reached.", analysis, RecoveryPolicy.RETRY, started)

    def _patch_recovery(
        self,
        analysis: FailureAnalysis,
        started: float,
        source_path: Path | None,
        validation_target: Path | None,
    ) -> RecoveryResult:
        patch = self.generate_patch(analysis, source_path)
        self.patcher.apply_patch(patch)
        success, output = self.validate_recovery(validation_target or patch.path)
        if not success:
            self.patcher.rollback(patch.path)
            return self._finish(
                False,
                "Patch failed validation and was rolled back.",
                analysis,
                RecoveryPolicy.PATCH,
                started,
                patch=patch,
                validation_output=output,
                errors=[output],
            )
        return self._finish(
            True,
            "Patch recovery succeeded.",
            analysis,
            RecoveryPolicy.PATCH,
            started,
            patch=patch,
            validation_output=output,
        )

    def _generate_with_registry(self, analysis: FailureAnalysis, payload: dict[str, Any]) -> Any:
        if self.registry_adapter is None:
            return None
        worker = self.registry_adapter.resolve_worker(self._task_for_category(analysis.category))
        if worker is None:
            return None
        result = worker.execute(payload)
        return result.result if isinstance(result, WorkerResult) else result

    def _task_for_category(self, category: str) -> str:
        if category in {"Syntax Error", "Import Error", "Validation Error", "Runtime Error"}:
            return "code_fix"
        if category == "Dependency Error":
            return "dependency_fix"
        return "recovery"

    def _coerce_patch(self, generated: Any, source_path: Path | None) -> RecoveryPatch:
        if isinstance(generated, RecoveryPatch):
            return generated
        if isinstance(generated, dict):
            path = generated.get("path") or source_path
            content = generated.get("content")
            summary = str(generated.get("summary", "Generated recovery patch."))
            if path and content:
                return RecoveryPatch(Path(path), str(content), summary)
        if isinstance(generated, str) and source_path is not None:
            return RecoveryPatch(source_path, self._strip_fences(generated), "Generated full-file patch.")
        raise HealingError("No usable recovery patch was generated.")

    def _strip_fences(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```python"):
            cleaned = cleaned.removeprefix("```python").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        return cleaned + ("\n" if cleaned and not cleaned.endswith("\n") else "")

    def _finish(
        self,
        success: bool,
        message: str,
        analysis: FailureAnalysis,
        strategy: str,
        started: float,
        retry_count: int = 0,
        patch: RecoveryPatch | None = None,
        validation_output: str = "",
        errors: list[str] | None = None,
    ) -> RecoveryResult:
        memory_reference = ""
        if success:
            memory_reference = self._store_success(analysis, strategy, retry_count, patch)
        entry = RecoveryHistoryEntry(
            original_error=analysis.original_error,
            recovery_action=strategy,
            retry_count=retry_count,
            success=success,
            execution_time=time.perf_counter() - started,
            patch_summary=patch.summary if patch else "",
            memory_reference=memory_reference,
        )
        self.history.add(entry)
        return RecoveryResult(
            success=success,
            message=message,
            analysis=analysis,
            strategy=strategy,
            retry_count=retry_count,
            patch=patch,
            validation_output=validation_output,
            history_entry=entry,
            errors=errors or [],
        )

    def _store_success(
        self,
        analysis: FailureAnalysis,
        strategy: str,
        retry_count: int,
        patch: RecoveryPatch | None,
    ) -> str:
        key = f"self_healing:{analysis.task_id}:{strategy}:{int(time.time() * 1000)}"
        self.memory_manager.save_memory(
            key,
            {
                "original_error": analysis.original_error,
                "category": analysis.category,
                "recovery_action": strategy,
                "retry_count": retry_count,
                "patch_summary": patch.summary if patch else "",
                "patch_path": str(patch.path) if patch else "",
            },
            tags=["self_healing", "successful_recovery"],
        )
        return key
