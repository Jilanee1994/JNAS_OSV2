"""Compile validation for generated Python projects."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildValidationResult:
    """Result of a compile validation run."""

    success: bool
    output: str
    return_code: int


class BuildValidator:
    """Run Python compile validation for generated files."""

    def validate(self, target: Path) -> BuildValidationResult:
        """Run `python -m compileall` and capture output."""
        completed = subprocess.run(
            [sys.executable, "-m", "compileall", str(target)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        return BuildValidationResult(
            success=completed.returncode == 0,
            output=output.strip(),
            return_code=completed.returncode,
        )
