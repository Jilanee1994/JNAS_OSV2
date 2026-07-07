"""Autonomous Builder Agent V3."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.executor import ExecutionResult
    from JNAS_AI_CORE.self_healing import SelfHealingEngine
except ImportError:
    ExecutionResult = None
    SelfHealingEngine = None

from .file_writer import BuilderFileWriter
from .generator_v3 import LLMGenerator
from .llm_interface import BuilderLLMClient
from .pipeline import BuilderPatchGenerator
from .project_creator_v3 import ProjectCreator
from .provider_factory_v3 import BuilderProviderFactory
from .report_v2 import SelfHealingAction
from .reporter_v3 import BuilderReporter, BuilderV3Report
from .utils import get_logger
from .validation_v3 import Compiler, PytestRunner
from .validator import ValidationResult


class BuilderPipeline:
    """Full Builder Agent V3 execution pipeline."""

    def __init__(
        self,
        workspace: Path | None = None,
        project_creator: ProjectCreator | None = None,
        generator: LLMGenerator | None = None,
        file_writer: BuilderFileWriter | None = None,
        compiler: Compiler | None = None,
        pytest_runner: PytestRunner | None = None,
        reporter: BuilderReporter | None = None,
        llm_client: BuilderLLMClient | None = None,
        self_healing_engine: Any | None = None,
        max_retries: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or get_logger(__name__)
        self.workspace = workspace or Path("workspace") / "generated_projects"
        self.llm_client = llm_client or BuilderLLMClient(router=BuilderProviderFactory(logger=self.logger).create_router())
        self.project_creator = project_creator or ProjectCreator(self.llm_client, logger=self.logger)
        self.generator = generator or LLMGenerator(self.llm_client, logger=self.logger)
        self.file_writer = file_writer or BuilderFileWriter()
        self.compiler = compiler or Compiler(logger=self.logger)
        self.pytest_runner = pytest_runner or PytestRunner(logger=self.logger)
        self.reporter = reporter or BuilderReporter()
        self.self_healing_engine = self_healing_engine
        self.max_retries = max_retries

    def run(self, user_prompt: str, git_commit: bool = False) -> BuilderV3Report:
        """Run Builder Agent V3 for a user prompt."""
        started = time.perf_counter()
        spec, plan_id = self.project_creator.create(user_prompt)
        project_root = self.file_writer.create_project_root(self.workspace, spec)
        report = BuilderV3Report(spec.name, project_root, plan_id=plan_id)
        try:
            self._generate_project(spec, project_root, report)
            self._validate_with_recovery(spec, project_root, report)
            if git_commit and report.final_result == "SUCCESS":
                report.git_commit = self._git_commit(project_root, spec.name)
        except Exception as exc:
            self.logger.exception("Builder V3 failed.")
            report.remaining_issues.append(str(exc))
        report.execution_time = time.perf_counter() - started
        self.reporter.write(report)
        return report

    def _generate_project(self, spec: Any, project_root: Path, report: BuilderV3Report) -> None:
        self.logger.info("Generate Project Structure Started.")
        for project_file in spec.files:
            response = self.generator.generate_file(spec, project_file)
            if not report.provider_used:
                report.provider_used = response.provider
            written = self.file_writer.write_file(project_root, project_file.path, response.content)
            report.files_created.append(written)
            self.logger.info("Write File Finished: %s.", written)
        self.logger.info("Generate Project Structure Finished.")

    def _validate_with_recovery(self, spec: Any, project_root: Path, report: BuilderV3Report) -> None:
        for attempt in range(self.max_retries + 1):
            compile_result = self.compiler.run(project_root)
            report.compile_result = compile_result
            if not compile_result.success:
                if attempt >= self.max_retries or not self._self_heal("compile", spec, project_root, compile_result, report):
                    report.remaining_issues.append("Compile failed after retry limit.")
                    return
                report.retries += 1
                continue

            pytest_result = self.pytest_runner.run(project_root)
            report.pytest_result = pytest_result
            if pytest_result.success:
                return
            if attempt >= self.max_retries or not self._self_heal("pytest", spec, project_root, pytest_result, report):
                report.remaining_issues.append("Pytest failed after retry limit.")
                return
            report.retries += 1

    def _self_heal(
        self,
        stage: str,
        spec: Any,
        project_root: Path,
        result: ValidationResult,
        report: BuilderV3Report,
    ) -> bool:
        if SelfHealingEngine is None or ExecutionResult is None:
            report.remaining_issues.append("Self-Healing unavailable.")
            return False
        source_path = self._source_path(project_root, result)
        engine = self.self_healing_engine or SelfHealingEngine(
            patch_generator=BuilderPatchGenerator(
                spec,
                project_root,
                self.generator.prompt_manager,
                self.llm_client,
                self.file_writer,
            )
        )
        failure = ExecutionResult(
            task_id=f"builder_v3:{stage}",
            success=False,
            output=result.output,
            error=result.output,
            duration=result.duration,
            metadata={"stage": stage, "project_root": str(project_root)},
        )
        recovery = engine.recover(
            failure,
            traceback_text=result.traceback or result.output,
            source_path=source_path,
            validation_target=project_root,
            metadata={"stage": stage},
        )
        report.self_healing_actions.append(
            SelfHealingAction(
                stage=stage,
                success=bool(recovery.success),
                message=str(recovery.message),
                strategy=str(recovery.strategy),
                source_path=source_path,
            )
        )
        return bool(recovery.success)

    def _source_path(self, project_root: Path, result: ValidationResult) -> Path:
        for failed in result.failed_files:
            candidate = failed if failed.is_absolute() else project_root / failed
            if candidate.exists():
                return candidate
        for path in project_root.rglob("*.py"):
            return path
        return project_root

    def _git_commit(self, project_root: Path, project_name: str) -> str:
        status = subprocess.run(["git", "status", "--short", str(project_root)], capture_output=True, text=True, check=False)
        if not status.stdout.strip():
            return "no-changes"
        subprocess.run(["git", "add", str(project_root)], capture_output=True, text=True, check=False)
        message = f"Build project: {project_name}"
        completed = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            return f"failed: {(completed.stderr or completed.stdout).strip()}"
        return message


class BuilderAgentV3:
    """Public facade for Builder Agent V3."""

    def __init__(self, pipeline: BuilderPipeline | None = None) -> None:
        self.pipeline = pipeline or BuilderPipeline()

    def build(self, user_prompt: str, git_commit: bool = False) -> BuilderV3Report:
        """Build one project from a user prompt."""
        return self.pipeline.run(user_prompt, git_commit=git_commit)
