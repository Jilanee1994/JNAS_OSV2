"""Compile and test validation for Builder Agent V1."""

from __future__ import annotations

import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class ValidationResult:
    """Validation outcome with failed files extracted from output."""

    success: bool
    output: str
    failed_files: list[Path] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    traceback: str = ""


class BuildValidator:
    """Run compile and pytest validation for generated projects."""

    _COMPILE_FILE_PATTERN = re.compile(r"\*\*\* Error compiling '([^']+)'")
    _PYTHON_FILE_PATTERN = re.compile(r'File "([^"]+\.py)"')
    _PYTEST_FILE_PATTERN = re.compile(r"FAILED\s+([^:\s]+)")
    _PYTEST_ERROR_PATTERN = re.compile(r"ERROR collecting\s+([^\n]+\.py)")

    def compile_project(self, project_root: Path) -> ValidationResult:
        """Run python -m compileall for a generated project."""
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, "-m", "compileall", str(project_root)],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        failed = [
            Path(match)
            for match in (
                self._COMPILE_FILE_PATTERN.findall(output)
                or self._PYTHON_FILE_PATTERN.findall(output)
            )
        ]
        success = completed.returncode == 0
        clean_output = output.strip()
        return ValidationResult(
            success,
            clean_output,
            failed,
            passed=1 if success else 0,
            failed=0 if success else 1,
            duration=time.perf_counter() - started,
            traceback="" if success else clean_output,
        )

    def test_project(self, project_root: Path) -> ValidationResult:
        """Run pytest for a generated project."""
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        failed = [
            Path(match.strip())
            for match in (
                self._PYTEST_FILE_PATTERN.findall(output)
                + self._PYTEST_ERROR_PATTERN.findall(output)
            )
        ]
        success = completed.returncode == 0
        clean_output = output.strip()
        passed_count, failed_count, skipped_count = self._extract_pytest_counts(clean_output)
        return ValidationResult(
            success,
            clean_output,
            failed,
            passed=passed_count,
            failed=failed_count,
            skipped=skipped_count,
            duration=time.perf_counter() - started,
            traceback="" if success else clean_output,
        )

    def _extract_pytest_counts(self, output: str) -> tuple[int, int, int]:
        passed = self._extract_count(output, "passed")
        failed = self._extract_count(output, "failed") + self._extract_count(output, "error")
        skipped = self._extract_count(output, "skipped")
        return passed, failed, skipped

    def _extract_count(self, output: str, label: str) -> int:
        matches = re.findall(rf"(\d+)\s+{re.escape(label)}", output, flags=re.IGNORECASE)
        return sum(int(match) for match in matches)
