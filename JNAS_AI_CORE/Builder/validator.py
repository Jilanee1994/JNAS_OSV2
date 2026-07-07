"""Compile and test validation for Builder Agent V1."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class ValidationResult:
    """Validation outcome with failed files extracted from output."""

    success: bool
    output: str
    failed_files: list[Path] = field(default_factory=list)


class BuildValidator:
    """Run compile and pytest validation for generated projects."""

    _COMPILE_FILE_PATTERN = re.compile(r"\*\*\* Error compiling '([^']+)'")
    _PYTHON_FILE_PATTERN = re.compile(r'File "([^"]+\.py)"')
    _PYTEST_FILE_PATTERN = re.compile(r"FAILED\s+([^:\s]+)")
    _PYTEST_ERROR_PATTERN = re.compile(r"ERROR collecting\s+([^\n]+\.py)")

    def compile_project(self, project_root: Path) -> ValidationResult:
        """Run python -m compileall for a generated project."""
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
        return ValidationResult(completed.returncode == 0, output.strip(), failed)

    def test_project(self, project_root: Path) -> ValidationResult:
        """Run pytest for a generated project."""
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
        return ValidationResult(completed.returncode == 0, output.strip(), failed)
