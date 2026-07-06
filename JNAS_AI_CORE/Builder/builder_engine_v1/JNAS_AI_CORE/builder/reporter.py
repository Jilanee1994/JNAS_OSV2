"""
builder.reporter
=================

Produces build reports (Markdown + in-memory structured data) and
prints a human-readable build summary to the console.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .tester import TestOutcome
from .utils import get_logger, write_text_file

__all__ = ["BuildReport", "BuildReporter"]


@dataclass
class BuildReport:
    """
    Structured record of a single module build.

    Attributes:
        module_name: Name of the module that was built.
        created_files: List of file paths created during the build.
        generation_errors: Any non-fatal errors encountered during
            code/test generation (fallbacks were used).
        test_outcome: The ``TestOutcome`` from running generated tests,
            or ``None`` if tests were not run.
        timestamp: UTC timestamp of when the build completed.
        success: Overall build success (files created AND tests passed).
    """

    module_name: str
    created_files: List[str] = field(default_factory=list)
    generation_errors: List[str] = field(default_factory=list)
    test_outcome: Optional[TestOutcome] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def success(self) -> bool:
        """Whether the build succeeded overall (tests passed, if run)."""
        if self.test_outcome is None:
            return not self.generation_errors
        return self.test_outcome.success and not self.generation_errors

    def to_markdown(self) -> str:
        """
        Render this build report as a Markdown document.

        Returns:
            Markdown-formatted report text.
        """
        lines: List[str] = [
            f"# Build Report: `{self.module_name}`",
            "",
            f"- **Timestamp (UTC):** {self.timestamp}",
            f"- **Overall status:** {'✅ SUCCESS' if self.success else '❌ FAILURE'}",
            "",
            "## Created Files",
        ]
        if self.created_files:
            lines.extend(f"- `{f}`" for f in self.created_files)
        else:
            lines.append("- _None_")

        lines += ["", "## Generation Errors"]
        if self.generation_errors:
            lines.extend(f"- {e}" for e in self.generation_errors)
        else:
            lines.append("- _None_")

        lines += ["", "## Test Results"]
        if self.test_outcome is None:
            lines.append("- Tests were not executed.")
        else:
            outcome = self.test_outcome
            lines.append(f"- **Status:** {'PASSED' if outcome.success else 'FAILED'}")
            lines.append(f"- **Passed:** {outcome.passed_count}")
            lines.append(f"- **Failed:** {outcome.failed_count}")
            if outcome.failure_summary:
                lines.append("- **Failures:**")
                lines.extend(f"  - `{f}`" for f in outcome.failure_summary)
            lines.append("")
            lines.append("### Raw pytest output")
            lines.append("```")
            lines.append(outcome.raw_result.stdout.strip() or "(no stdout)")
            if outcome.raw_result.stderr.strip():
                lines.append("--- stderr ---")
                lines.append(outcome.raw_result.stderr.strip())
            lines.append("```")

        return "\n".join(lines) + "\n"


class BuildReporter:
    """
    Generates and persists ``BuildReport`` objects, and prints
    human-readable summaries to the console/log.

    Single responsibility: reporting. Does not generate code or run
    tests itself.
    """

    def __init__(
        self,
        reports_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize the BuildReporter.

        Args:
            reports_dir: Directory where Markdown reports are saved.
                Defaults to ``<cwd>/logs/build_reports``.
            logger: Optional logger override.
        """
        self.reports_dir = reports_dir or Path("logs") / "build_reports"
        self.logger = logger or get_logger(__name__)

    def save_report(self, report: BuildReport) -> Path:
        """
        Persist a ``BuildReport`` as a Markdown file.

        Args:
            report: The build report to persist.

        Returns:
            The path the report was written to.

        Raises:
            OSError: If the report cannot be written to disk.
        """
        filename = f"{report.module_name}_build_report.md"
        path = self.reports_dir / filename
        try:
            write_text_file(path, report.to_markdown())
            self.logger.info("Build report saved to %s", path)
        except OSError as exc:
            self.logger.error("Failed to save build report to %s: %s", path, exc)
            raise
        return path

    def print_summary(self, report: BuildReport) -> None:
        """
        Print a concise, human-readable build summary to stdout/log.

        Args:
            report: The build report to summarize.
        """
        status = "SUCCESS" if report.success else "FAILURE"
        divider = "=" * 60
        lines = [
            divider,
            f"BUILD SUMMARY: {report.module_name}",
            divider,
            f"Status        : {status}",
            f"Files created : {len(report.created_files)}",
        ]
        for f in report.created_files:
            lines.append(f"  - {f}")

        if report.test_outcome is not None:
            outcome = report.test_outcome
            lines.append(
                f"Tests         : {outcome.passed_count} passed, "
                f"{outcome.failed_count} failed"
            )
            if outcome.failure_summary:
                lines.append("Failures      :")
                for failure in outcome.failure_summary:
                    lines.append(f"  - {failure}")
        else:
            lines.append("Tests         : not executed")

        if report.generation_errors:
            lines.append("Generation errors:")
            for err in report.generation_errors:
                lines.append(f"  - {err}")

        lines.append(divider)
        summary_text = "\n".join(lines)
        print(summary_text)
        self.logger.info("Build summary:\n%s", summary_text)
