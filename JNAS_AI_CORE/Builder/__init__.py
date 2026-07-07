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

from .builder_agent import BuilderAgent, BuilderAgentReport
from .builder import BuilderEngine, main
from .file_writer import BuilderFileWriter
from .generator import CodeGenerator
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager
from .reporter import BuildReport, BuildReporter
from .tester import TestOutcome, TestRunner
from .validator import BuildValidator, ValidationResult

__all__ = [
    "BuilderAgent",
    "BuilderAgentReport",
    "BuilderEngine",
    "BuilderFileWriter",
    "BuilderPromptManager",
    "CodeGenerator",
    "ProjectFile",
    "ProjectSpec",
    "BuildValidator",
    "TestRunner",
    "TestOutcome",
    "BuildReporter",
    "BuildReport",
    "ValidationResult",
    "main",
]

__version__ = "1.0.0"
