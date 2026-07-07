"""Build report model for Builder Agent V2."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .validator import ValidationResult


@dataclass
class SelfHealingAction:
    """Recorded self-healing action from a Builder V2 run."""

    stage: str
    success: bool
    message: str
    strategy: str = ""
    source_path: Path | None = None


@dataclass
class BuilderV2Report:
    """Structured V2 build report."""

    project_name: str
    project_root: Path
    files_created: list[Path] = field(default_factory=list)
    files_modified: list[Path] = field(default_factory=list)
    provider: str = ""
    plan_id: str = ""
    compile_result: ValidationResult | None = None
    test_result: ValidationResult | None = None
    self_healing_actions: list[SelfHealingAction] = field(default_factory=list)
    remaining_issues: list[str] = field(default_factory=list)
    execution_time: float = 0.0

    @property
    def success(self) -> bool:
        """Return whether the build completed successfully."""
        return bool(
            self.compile_result
            and self.compile_result.success
            and self.test_result
            and self.test_result.success
            and not self.remaining_issues
        )

    def to_markdown(self) -> str:
        """Render the V2 report as Markdown."""
        lines = [
            f"# BUILD REPORT: {self.project_name}",
            "",
            "## Build Summary",
            "",
            f"- Status: {'SUCCESS' if self.success else 'FAILED'}",
            f"- Project root: `{self.project_root}`",
            f"- Provider: `{self.provider or 'unknown'}`",
            f"- Plan ID: `{self.plan_id or 'not-created'}`",
            f"- Execution time: {self.execution_time:.2f}s",
            "",
            "## Files Created",
        ]
        lines.extend(f"- `{path}`" for path in self.files_created) if self.files_created else lines.append("- None")
        lines.extend(["", "## Files Modified"])
        lines.extend(f"- `{path}`" for path in self.files_modified) if self.files_modified else lines.append("- None")
        lines.extend(["", "## Compile Results", ""])
        lines.extend(self._validation_lines(self.compile_result))
        lines.extend(["", "## Test Results", ""])
        lines.extend(self._validation_lines(self.test_result))
        lines.extend(["", "## Self-Healing Actions"])
        if self.self_healing_actions:
            for action in self.self_healing_actions:
                path = f" `{action.source_path}`" if action.source_path else ""
                lines.append(
                    f"- {action.stage}: {'SUCCESS' if action.success else 'FAILED'}"
                    f"{path} - {action.message}"
                )
        else:
            lines.append("- None")
        lines.extend(["", "## Remaining Issues"])
        lines.extend(f"- {issue}" for issue in self.remaining_issues) if self.remaining_issues else lines.append("- None")
        return "\n".join(lines) + "\n"

    def _validation_lines(self, result: ValidationResult | None) -> list[str]:
        if result is None:
            return ["- Not run"]
        lines = [
            f"- Status: {'PASS' if result.success else 'FAIL'}",
            f"- Passed: {result.passed}",
            f"- Failed: {result.failed}",
            f"- Skipped: {result.skipped}",
            f"- Execution time: {result.duration:.2f}s",
        ]
        if result.failed_files:
            lines.append("- Failed files:")
            lines.extend(f"  - `{path}`" for path in result.failed_files)
        if result.output:
            lines.extend(["", "```text", result.output, "```"])
        return lines
