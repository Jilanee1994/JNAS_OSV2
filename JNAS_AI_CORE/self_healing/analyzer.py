"""Failure analysis for self-healing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from JNAS_AI_CORE.executor import ExecutionResult
except ImportError:
    from executor import ExecutionResult


@dataclass
class FailureAnalysis:
    """Structured analysis of a failed execution."""

    task_id: str
    original_error: str
    traceback: str
    category: str
    metadata: dict[str, Any] = field(default_factory=dict)


class FailureAnalyzer:
    """Convert failed execution results into fix requests."""

    def analyze(
        self,
        failure: ExecutionResult,
        traceback_text: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> FailureAnalysis:
        """Analyze a failed execution result."""
        if failure.success:
            raise ValueError("FailureAnalyzer requires an unsuccessful ExecutionResult.")

        error = failure.error or "Unknown execution failure."
        category = self.classify_error(error, traceback_text)
        return FailureAnalysis(
            task_id=failure.task_id,
            original_error=error,
            traceback=traceback_text,
            category=category,
            metadata=metadata or {},
        )

    def classify_error(self, error: str, traceback_text: str = "") -> str:
        """Classify an error into a recovery category."""
        combined = f"{error}\n{traceback_text}".lower()
        if "syntaxerror" in combined or "indentationerror" in combined:
            return "Syntax Error"
        if "no module named" in combined:
            return "Dependency Error"

        if "modulenotfounderror" in combined:
            return "Dependency Error"

        if "cannot import name" in combined:
            return "Import Error"

        if "importerror" in combined:
            return "Import Error"

        if "nameerror" in combined or "notimplementederror" in combined:
            return "Runtime Error"

        if "nameerror" in combined or "notimplementederror" in combined:
            return "Runtime Error"
        if "validation" in combined or "valueerror" in combined:
            return "Validation Error"
        if "config" in combined or "setting" in combined:
            return "Configuration Error"
        if "filenotfounderror" in combined or "permissionerror" in combined or "oserror" in combined:
            return "Filesystem Error"
        if "assertionerror" in combined:
            return "Validation Error"
        if "runtimeerror" in combined or "exception" in combined:
            return "Runtime Error"
        return "Unknown Error"
