"""
Builder Engine v1 for JNAS_AI_CORE.

Automatically scaffolds new modules (folder, source file, prompt
artifact, and unit tests), using the project's existing LLMManager,
FileTool, ProjectReader, ProjectScanner, ContextBuilder, and CodeAgent
components.

Public API:
    - ``BuilderEngine``: top-level orchestrator.
    - ``CodeGenerator``: LLM-backed code/test/prompt generation.
    - ``TestRunner`` / ``TestOutcome``: pytest execution and results.
    - ``BuildReporter`` / ``BuildReport``: build reporting and summaries.
"""

from __future__ import annotations

from .builder import BuilderEngine, main
from .generator import CodeGenerator
from .reporter import BuildReport, BuildReporter
from .tester import TestOutcome, TestRunner

__all__ = [
    "BuilderEngine",
    "CodeGenerator",
    "TestRunner",
    "TestOutcome",
    "BuildReporter",
    "BuildReport",
    "main",
]

__version__ = "1.0.0"
