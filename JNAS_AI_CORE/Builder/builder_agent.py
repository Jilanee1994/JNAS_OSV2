"""Autonomous project Builder Agent V1."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .file_writer import BuilderFileWriter
from .generation_validator import GenerationValidator
from .llm_interface import BuilderLLMClient
from .pipeline import BuilderExecutionPipeline
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager
from .report_v2 import BuilderV2Report
from .specification_validator import SpecificationValidator, SpecificationValidationResult
from .utils import call_flexible, get_logger, write_text_file
from .validator import BuildValidator, ValidationResult

try:
    from JNAS_AI_CORE.llm.manager import LLMManager
except ImportError:
    LLMManager = None


@dataclass
class BuilderAgentReport:
    """Structured report for a generated project build."""

    project_name: str
    project_root: Path
    generated_files: list[Path] = field(default_factory=list)
    prompts: dict[str, str] = field(default_factory=dict)
    retries: int = 0
    compile_result: ValidationResult | None = None
    test_result: ValidationResult | None = None
    specification_result: SpecificationValidationResult | None = None
    generation_validation_errors: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def success(self) -> bool:
        """Return whether compile and tests passed."""
        return bool(
            self.compile_result
            and self.compile_result.success
            and self.test_result
            and self.test_result.success
            and not self.errors
        )

    def to_markdown(self) -> str:
        """Render the report as Markdown."""
        lines = [
            f"# BUILD REPORT: {self.project_name}",
            "",
            f"- Project root: `{self.project_root}`",
            f"- Status: {'SUCCESS' if self.success else 'FAILED'}",
            f"- Duration: {self.duration:.2f}s",
            f"- Retries: {self.retries}",
            "",
            "## Generated Files",
        ]
        lines.extend(f"- `{path}`" for path in self.generated_files) if self.generated_files else lines.append("- None")
        lines.extend(["", "## Specification", ""])
        if self.specification_result is None:
            lines.append("- No explicit file specification enforced.")
        else:
            lines.append("PASS" if self.specification_result.success else "FAIL")
            lines.extend(["", "```text", self.specification_result.to_message(), "```"])
        lines.extend(["", "## Generation Validation", ""])
        if self.generation_validation_errors:
            for path, errors in self.generation_validation_errors.items():
                lines.append(f"- `{path}`")
                lines.extend(f"  - {error}" for error in errors)
        else:
            lines.append("- PASS")
        lines.extend(["", "## Compile Result", ""])
        lines.append("PASS" if self.compile_result and self.compile_result.success else "FAIL")
        if self.compile_result and self.compile_result.output:
            lines.extend(["", "```text", self.compile_result.output, "```"])
        lines.extend(["", "## Test Result", ""])
        lines.append("PASS" if self.test_result and self.test_result.success else "FAIL")
        if self.test_result and self.test_result.output:
            lines.extend(["", "```text", self.test_result.output, "```"])
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in self.errors) if self.errors else lines.append("- None")
        return "\n".join(lines) + "\n"


class BuilderAgent:
    """Create complete software projects through file-by-file Ollama generation."""

    _LLM_METHODS = ("generate", "generate_code", "complete", "chat", "run")

    def __init__(
        self,
        llm_manager: Any | None = None,
        workspace: Path | None = None,
        file_writer: BuilderFileWriter | None = None,
        prompt_manager: BuilderPromptManager | None = None,
        validator: BuildValidator | None = None,
        specification_validator: SpecificationValidator | None = None,
        generation_validator: GenerationValidator | None = None,
        llm_client: BuilderLLMClient | None = None,
        planner: Any | None = None,
        self_healing_engine: Any | None = None,
        retry_limit: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        self.llm_manager = llm_manager or (LLMManager() if LLMManager is not None else None)
        self.workspace = workspace or Path("workspace") / "generated_projects"
        self.file_writer = file_writer or BuilderFileWriter()
        self.prompt_manager = prompt_manager or BuilderPromptManager()
        self.validator = validator or BuildValidator()
        self.specification_validator = specification_validator or SpecificationValidator()
        self.generation_validator = generation_validator or GenerationValidator()
        self.llm_client = llm_client
        self.planner = planner
        self.self_healing_engine = self_healing_engine
        self.retry_limit = retry_limit
        self.logger = logger or get_logger(__name__)

    def build_project(self, specification: str | dict[str, Any]) -> BuilderAgentReport:
        """Build a complete project from a project specification."""
        if self.llm_manager is None:
            raise RuntimeError("BuilderAgent.build_project requires LLMManager or compatible llm_manager.")
        started = time.perf_counter()
        spec = self._project_spec_for(specification)
        project_root = self.file_writer.create_project_root(self.workspace, spec)
        report = BuilderAgentReport(spec.name, project_root)
        report.specification_result = self._validate_specification(specification, spec)
        try:
            self._generate_all_files(spec, project_root, report)
            self._validate_and_repair(spec, project_root, report)
        except Exception as exc:
            report.errors.append(str(exc))
            self.logger.exception("BuilderAgent failed.")
        report.duration = time.perf_counter() - started
        self._save_report(report)
        return report

    def execute(self, specification: str | dict[str, Any]) -> BuilderV2Report:
        """Execute the Builder Agent V2 autonomous project pipeline."""
        llm_client = self.llm_client or BuilderLLMClient()
        pipeline = BuilderExecutionPipeline(
            workspace=self.workspace,
            file_writer=self.file_writer,
            prompt_manager=self.prompt_manager,
            validator=self.validator,
            llm_client=llm_client,
            planner=self.planner,
            self_healing_engine=self.self_healing_engine,
            retry_limit=self.retry_limit,
            logger=self.logger,
        )
        return pipeline.execute(specification)

    def _generate_all_files(self, spec: ProjectSpec, project_root: Path, report: BuilderAgentReport) -> None:
        for project_file in spec.files:
            prompt = self.prompt_manager.build_file_prompt(spec, project_file)
            report.prompts[project_file.path.as_posix()] = prompt
            content = self._generate_valid_file(spec, project_file, prompt, report)
            written = self.file_writer.write_file(project_root, project_file.path, content)
            report.generated_files.append(written)

    def _generate_valid_file(
        self,
        spec: ProjectSpec,
        project_file: ProjectFile,
        prompt: str,
        report: BuilderAgentReport,
    ) -> str:
        current_prompt = prompt
        last_errors: list[str] = []
        for attempt in range(self.retry_limit + 1):
            content = self._ask_ollama(current_prompt)
            result = self.generation_validator.validate(spec, project_file, content)
            if result.success:
                return content
            last_errors = result.errors
            report.generation_validation_errors[project_file.path.as_posix()] = result.errors
            if attempt >= self.retry_limit:
                break
            current_prompt = self.prompt_manager.build_generation_correction_prompt(
                spec,
                project_file,
                content,
                result.to_message(),
            )
            report.retries += 1
        raise ValueError(f"Generated content failed validation for {project_file.path}: {'; '.join(last_errors)}")

    def _project_spec_for(self, specification: str | dict[str, Any]) -> ProjectSpec:
        if isinstance(specification, str):
            expected = self.specification_validator.expected_from_prompt(specification)
            if expected is not None:
                return expected.to_project_spec()
        return ProjectSpec.from_input(specification)

    def _validate_specification(
        self,
        specification: str | dict[str, Any],
        spec: ProjectSpec,
    ) -> SpecificationValidationResult | None:
        if not isinstance(specification, str):
            return None
        expected = self.specification_validator.expected_from_prompt(specification)
        if expected is None:
            return None
        return self.specification_validator.validate_project_spec(expected, spec)

    def _validate_and_repair(self, spec: ProjectSpec, project_root: Path, report: BuilderAgentReport) -> None:
        for attempt in range(self.retry_limit + 1):
            compile_result = self.validator.compile_project(project_root)
            report.compile_result = compile_result
            if not compile_result.success:
                if attempt >= self.retry_limit:
                    report.errors.append("Compile validation failed after retry limit.")
                    return
                self._repair_failed_files(spec, project_root, compile_result, report)
                continue

            test_result = self.validator.test_project(project_root)
            report.test_result = test_result
            if test_result.success:
                return
            if attempt >= self.retry_limit:
                report.errors.append("Pytest validation failed after retry limit.")
                return
            self._repair_failed_files(spec, project_root, test_result, report)

    def _repair_failed_files(
        self,
        spec: ProjectSpec,
        project_root: Path,
        validation_result: ValidationResult,
        report: BuilderAgentReport,
    ) -> None:
        failed_files = self._resolve_failed_files(spec, project_root, validation_result)
        for project_file in failed_files:
            current = self.file_writer.read_file(project_root, project_file.path)
            prompt = self.prompt_manager.build_repair_prompt(spec, project_file, current, validation_result.output)
            content = self._generate_valid_file(spec, project_file, prompt, report)
            self.file_writer.write_file(project_root, project_file.path, content)
            report.retries += 1

    def _resolve_failed_files(
        self,
        spec: ProjectSpec,
        project_root: Path,
        validation_result: ValidationResult,
    ) -> list[ProjectFile]:
        by_path = {item.path.as_posix(): item for item in spec.files}
        resolved: list[ProjectFile] = []
        for failed in validation_result.failed_files:
            relative = failed
            if failed.is_absolute():
                try:
                    relative = failed.relative_to(project_root)
                except ValueError:
                    continue
            match = by_path.get(relative.as_posix())
            if match is not None:
                resolved.append(match)
        if resolved:
            return resolved
        return [item for item in spec.files if item.path.suffix == ".py"][:1]

    def _ask_ollama(self, prompt: str) -> str:
        result = call_flexible(self.llm_manager, self._LLM_METHODS, prompt)
        return str(result)

    def _save_report(self, report: BuilderAgentReport) -> Path:
        path = report.project_root / "BUILD_REPORT.md"
        write_text_file(path, report.to_markdown())
        return path


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for build_project."""
    parser = argparse.ArgumentParser(prog="build_project", description="Build a project with JNAS Builder Agent V1.")
    parser.add_argument("specification", help="Project name or project specification text.")
    parser.add_argument("--workspace", type=Path, default=None, help="Directory where generated projects are created.")
    parser.add_argument("--retry-limit", type=int, default=3, help="Maximum repair attempts.")
    args = parser.parse_args(argv)
    agent = BuilderAgent(workspace=args.workspace, retry_limit=args.retry_limit)
    report = agent.build_project(args.specification)
    print(report.to_markdown())
    return 0 if report.success else 1


if __name__ == "__main__":
    sys.exit(main())
