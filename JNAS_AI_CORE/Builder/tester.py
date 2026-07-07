"""
builder.tester
==============

Executes pytest against generated modules and captures structured
pass/fail results for the Builder Engine's reporting stage.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .utils import PytestResult, get_logger, run_pytest

__all__ = ["TestOutcome", "TestRunner"]


@dataclass
class TestOutcome:
    """
    Structured, human- and machine-readable outcome of a test run for
    a single generated module.

    Attributes:
        module_name: Name of the module that was tested.
        success: Whether all tests passed (return code 0).
        passed_count: Number of tests that passed.
        failed_count: Number of tests that failed.
        raw_result: The underlying ``PytestResult``.
        failure_summary: Extracted failure lines, if any.
    """

    __test__ = False  # tell pytest this is not a test class despite the name

    module_name: str
    success: bool
    passed_count: int
    failed_count: int
    raw_result: PytestResult
    failure_summary: List[str] = field(default_factory=list)


class TestRunner:
    """
    Runs pytest against a generated module's test file and parses the
    results into a structured ``TestOutcome``.

    Single responsibility: test execution and result parsing. Does not
    generate tests (see ``CodeGenerator``) or produce build reports
    (see ``BuilderEngine`` / ``BuildReporter``).
    """

    __test__ = False  # tell pytest this is not a test class despite the name

    _SUMMARY_LINE_PATTERN = re.compile(
        r"(\d+) passed"
        r"(?:, (\d+) failed)?"
        r"(?:, (\d+) error(?:s)?)?",
    )
    _FAILED_TEST_PATTERN = re.compile(r"^FAILED\s+(.+)$", re.MULTILINE)

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the TestRunner.

        Args:
            logger: Optional logger override.
        """
        self.logger = logger or get_logger(__name__)

    def run(self, module_name: str, test_path: Path) -> TestOutcome:
        """
        Execute pytest against a module's generated test file.

        Args:
            module_name: Name of the module under test.
            test_path: Path to the test file or directory.

        Returns:
            A ``TestOutcome`` summarizing pass/fail counts and any
            captured failure details.
        """
        self.logger.info("Running tests for module '%s' at %s", module_name, test_path)
        result = run_pytest(test_path)

        passed, failed = self._parse_counts(result.stdout)
        failures = self._parse_failures(result.stdout)

        outcome = TestOutcome(
            module_name=module_name,
            success=result.success,
            passed_count=passed,
            failed_count=failed,
            raw_result=result,
            failure_summary=failures,
        )

        if outcome.success:
            self.logger.info(
                "Tests PASSED for '%s' (%d passed).", module_name, outcome.passed_count
            )
        else:
            self.logger.warning(
                "Tests FAILED for '%s' (%d passed, %d failed). Failures: %s",
                module_name,
                outcome.passed_count,
                outcome.failed_count,
                outcome.failure_summary or [result.stderr[:200]],
            )
        return outcome

    def _parse_counts(self, stdout: str) -> tuple[int, int]:
        """
        Parse pytest's summary line to extract passed/failed counts.

        Args:
            stdout: Captured pytest stdout.

        Returns:
            A ``(passed, failed)`` tuple. Defaults to ``(0, 0)`` if no
            summary line is found.
        """
        match = self._SUMMARY_LINE_PATTERN.search(stdout)
        if not match:
            return 0, 0
        passed = int(match.group(1) or 0)
        failed = int(match.group(2) or 0) + int(match.group(3) or 0)
        return passed, failed

    def _parse_failures(self, stdout: str) -> List[str]:
        """
        Extract individual ``FAILED ...`` lines from pytest output.

        Args:
            stdout: Captured pytest stdout.

        Returns:
            A list of failure identifier strings (may be empty).
        """
        return self._FAILED_TEST_PATTERN.findall(stdout)
