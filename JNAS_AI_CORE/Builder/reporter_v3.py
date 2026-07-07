"""Reporting for Builder Agent V3."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .report_v2 import SelfHealingAction
from .utils import write_text_file
from .validator import ValidationResult


@dataclass
class BuilderV3Report:
    """Structured report for Builder Agent V3."""

    project_name: str
    project_root: Path
    provider_used: str = ""
    plan_id: str = ""
    files_created: list[Path] = field(default_factory=list)
    compile_result: ValidationResult | None = None
    pytest_result: ValidationResult | None = None
    retries: int = 0
    self_healing_actions: list[SelfHealingAction] = field(default_factory=list)
    execution_time: float = 0.0
    git_commit: str = ""
    remaining_issues: list[str] = field(default_factory=list)

    @property
    def final_result(self) -> str:
        """Return the final build result."""
        if self.compile_result and self.compile_result.success and self.pytest_result and self.pytest_result.success and not self.remaining_issues:
            return "SUCCESS"
        return "FAILED"


class BuilderReporter:
    """Persist Builder V3 reports."""

    def write(self, report: BuilderV3Report) -> Path:
        """Write BUILD_REPORT.md into the generated project."""
        path = report.project_root / "BUILD_REPORT.md"
        write_text_file(path, self.render(report))
        return path

    def render(self, report: BuilderV3Report) -> str:
        """Render report markdown."""
        lines = [
            f"# BUILD REPORT: {report.project_name}",
            "",
            f"- Project Name: {report.project_name}",
            f"- Provider Used: {report.provider_used or 'unknown'}",
            f"- Project Root: `{report.project_root}`",
            f"- Plan ID: `{report.plan_id or 'not-created'}`",
            f"- Retries: {report.retries}",
            f"- Execution Time: {report.execution_time:.2f}s",
            f"- Final Result: {report.final_result}",
            f"- Git Commit: {report.git_commit or 'not-requested'}",
            "",
            "## Files Created",
        ]
        lines.extend(f"- `{path}`" for path in report.files_created) if report.files_created else lines.append("- None")
        lines.extend(["", "## Compile Status"])
        lines.extend(self._validation_lines(report.compile_result))
        lines.extend(["", "## Pytest Status"])
        lines.extend(self._validation_lines(report.pytest_result))
        lines.extend(["", "## Self-Healing Actions"])
        if report.self_healing_actions:
            for action in report.self_healing_actions:
                lines.append(f"- {action.stage}: {'SUCCESS' if action.success else 'FAILED'} - {action.message}")
        else:
            lines.append("- None")
        lines.extend(["", "## Remaining Issues"])
        lines.extend(f"- {issue}" for issue in report.remaining_issues) if report.remaining_issues else lines.append("- None")
        return "\n".join(lines) + "\n"

    def _validation_lines(self, result: ValidationResult | None) -> list[str]:
        if result is None:
            return ["- Status: NOT RUN"]
        lines = [
            f"- Status: {'PASS' if result.success else 'FAIL'}",
            f"- Passed: {result.passed}",
            f"- Failed: {result.failed}",
            f"- Skipped: {result.skipped}",
            f"- Execution Time: {result.duration:.2f}s",
        ]
        if result.output:
            lines.extend(["", "```text", result.output, "```"])
        return lines
