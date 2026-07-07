"""Validation stages for Builder Agent V3."""

from __future__ import annotations

import logging
from pathlib import Path

from .validator import BuildValidator, ValidationResult


class Compiler:
    """Compile generated projects."""

    def __init__(self, validator: BuildValidator | None = None, logger: logging.Logger | None = None) -> None:
        self.validator = validator or BuildValidator()
        self.logger = logger or logging.getLogger(__name__)

    def run(self, project_root: Path) -> ValidationResult:
        """Run python -m compileall."""
        self.logger.info("Compile Started.")
        result = self.validator.compile_project(project_root)
        self.logger.info("Compile %s.", "Passed" if result.success else "Failed")
        return result


class PytestRunner:
    """Run pytest for generated projects."""

    def __init__(self, validator: BuildValidator | None = None, logger: logging.Logger | None = None) -> None:
        self.validator = validator or BuildValidator()
        self.logger = logger or logging.getLogger(__name__)

    def run(self, project_root: Path) -> ValidationResult:
        """Run pytest."""
        self.logger.info("Pytest Started.")
        result = self.validator.test_project(project_root)
        self.logger.info("Pytest %s.", "Passed" if result.success else "Failed")
        return result
