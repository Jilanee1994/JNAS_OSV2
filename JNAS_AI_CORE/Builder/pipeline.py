"""Execution pipeline for Builder Agent V2."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.executor import ExecutionResult
    from JNAS_AI_CORE.planner import Planner
    from JNAS_AI_CORE.self_healing import SelfHealingEngine
except ImportError:
    ExecutionResult = None
    Planner = None
    SelfHealingEngine = None

from .file_writer import BuilderFileWriter
from .llm_interface import BuilderLLMClient
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager
from .report_v2 import BuilderV2Report, SelfHealingAction
from .utils import get_logger, write_text_file
from .validator import BuildValidator, ValidationResult


class BuilderPatchGenerator:
    """Patch generator adapter used by the existing Self-Healing Engine."""

    def __init__(
        self,
        spec: ProjectSpec,
        project_root: Path,
        prompt_manager: BuilderPromptManager,
        llm_client: BuilderLLMClient,
        file_writer: BuilderFileWriter,
    ) -> None:
        self.spec = spec
        self.project_root = project_root
        self.prompt_manager = prompt_manager
        self.llm_client = llm_client
        self.file_writer = file_writer

    def generate_patch(self, payload: dict[str, Any]) -> dict[str, str]:
        """Generate a full-file patch for Self-Healing."""
        source_path = Path(payload.get("source_path") or "")
        project_file = self._project_file_for(source_path)
        current = self.file_writer.read_file(self.project_root, project_file.path)
        analysis = payload.get("analysis", {})
        errors = "\n".join(
            part
            for part in (
                str(analysis.get("original_error", "")),
                str(analysis.get("traceback", "")),
            )
            if part
        )
        prompt = self.prompt_manager.build_repair_prompt(self.spec, project_file, current, errors)
        response = self.llm_client.generate(prompt)
        return {
            "path": str(self.project_root / project_file.path),
            "content": response.content,
            "summary": f"Regenerated {project_file.path.as_posix()} through Builder V2 self-healing.",
        }

    def _project_file_for(self, source_path: Path) -> ProjectFile:
        try:
            relative = source_path.resolve().relative_to(self.project_root.resolve())
        except (OSError, ValueError):
            relative = source_path
        for project_file in self.spec.files:
            if project_file.path == relative:
                return project_file
        for project_file in self.spec.files:
            if project_file.path.suffix == ".py":
                return project_file
        raise ValueError("No Python file is available for self-healing.")


class BuilderExecutionPipeline:
    """Autonomous Builder Agent V2 execution pipeline."""

    def __init__(
        self,
        workspace: Path,
        file_writer: BuilderFileWriter,
        prompt_manager: BuilderPromptManager,
        validator: BuildValidator,
        llm_client: BuilderLLMClient,
        planner: Any | None = None,
        self_healing_engine: Any | None = None,
        retry_limit: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        self.workspace = workspace
        self.file_writer = file_writer
        self.prompt_manager = prompt_manager
        self.validator = validator
        self.llm_client = llm_client
        self.planner = planner if planner is not None else (Planner() if Planner is not None else None)
        self.self_healing_engine = self_healing_engine
        self.retry_limit = retry_limit
        self.logger = logger or get_logger(__name__)

    def execute(self, specification: str | dict[str, Any]) -> BuilderV2Report:
        """Execute the full Builder V2 workflow."""
        started = time.perf_counter()
        spec = ProjectSpec.from_input(specification)
        project_root = self.file_writer.create_project_root(self.workspace, spec)
        report = BuilderV2Report(spec.name, project_root)
        try:
            self._create_plan(spec, report)
            self._generate_files(spec, project_root, report)
            self._validate_with_recovery(spec, project_root, report)
        except Exception as exc:
            self.logger.exception("Builder V2 execution failed.")
            report.remaining_issues.append(str(exc))
        report.execution_time = time.perf_counter() - started
        self._save_report(report)
        return report

    def _create_plan(self, spec: ProjectSpec, report: BuilderV2Report) -> None:
        self.logger.info("Planner Started.")
        if self.planner is None:
            self.logger.warning("Planner unavailable; continuing with ProjectSpec.")
            return
        plan = self.planner.create_plan(spec.description or spec.name)
        report.plan_id = str(getattr(plan, "plan_id", ""))
        self.logger.info("Planner Finished.")

    def _generate_files(self, spec: ProjectSpec, project_root: Path, report: BuilderV2Report) -> None:
        self.logger.info("Builder Started.")
        for project_file in spec.files:
            prompt = self.prompt_manager.build_file_prompt(spec, project_file)
            response = self.llm_client.generate(prompt)
            if not report.provider:
                report.provider = response.provider
            written = self.file_writer.write_file(project_root, project_file.path, response.content)
            report.files_created.append(written)
            self.logger.info("File Created: %s.", written)

    def _validate_with_recovery(self, spec: ProjectSpec, project_root: Path, report: BuilderV2Report) -> None:
        for attempt in range(self.retry_limit + 1):
            self.logger.info("Compile Started.")
            compile_result = self.validator.compile_project(project_root)
            report.compile_result = compile_result
            if not compile_result.success:
                self.logger.warning("Compile Failed.")
                if attempt >= self.retry_limit or not self._heal("compile", spec, project_root, compile_result, report):
                    report.remaining_issues.append("Compile validation failed.")
                    return
                continue
            self.logger.info("Compile Passed.")

            self.logger.info("Pytest Started.")
            test_result = self.validator.test_project(project_root)
            report.test_result = test_result
            if test_result.success:
                self.logger.info("Pytest Passed.")
                self.logger.info("Build Finished.")
                return
            self.logger.warning("Pytest Failed.")
            if attempt >= self.retry_limit or not self._heal("pytest", spec, project_root, test_result, report):
                report.remaining_issues.append("Pytest validation failed.")
                return

    def _heal(
        self,
        stage: str,
        spec: ProjectSpec,
        project_root: Path,
        result: ValidationResult,
        report: BuilderV2Report,
    ) -> bool:
        if SelfHealingEngine is None or ExecutionResult is None:
            report.remaining_issues.append("Self-Healing Engine is unavailable.")
            return False
        engine = self.self_healing_engine or self._create_self_healing_engine(spec, project_root)
        source_path = self._source_path_for_failure(spec, project_root, result)
        failure = ExecutionResult(
            task_id=f"builder_v2:{stage}",
            success=False,
            output=result.output,
            error=result.output or f"{stage} validation failed.",
            duration=result.duration,
            metadata={"stage": stage, "project_root": str(project_root)},
        )
        recovery = engine.recover(
            failure,
            traceback_text=result.traceback or result.output,
            source_path=source_path,
            validation_target=project_root,
            metadata={"stage": stage, "failed_files": [str(path) for path in result.failed_files]},
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
        if recovery.success and recovery.patch is not None:
            report.files_modified.append(Path(recovery.patch.path))
        return bool(recovery.success)

    def _create_self_healing_engine(self, spec: ProjectSpec, project_root: Path) -> Any:
        patch_generator = BuilderPatchGenerator(
            spec,
            project_root,
            self.prompt_manager,
            self.llm_client,
            self.file_writer,
        )
        return SelfHealingEngine(patch_generator=patch_generator)

    def _source_path_for_failure(self, spec: ProjectSpec, project_root: Path, result: ValidationResult) -> Path:
        for failed in result.failed_files:
            if failed.is_absolute():
                return failed
            candidate = project_root / failed
            if candidate.exists():
                return candidate
        for project_file in spec.files:
            if project_file.path.suffix == ".py":
                return project_root / project_file.path
        return project_root

    def _save_report(self, report: BuilderV2Report) -> Path:
        path = report.project_root / "BUILD_REPORT.md"
        write_text_file(path, report.to_markdown())
        return path
