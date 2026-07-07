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
from .builder_v3 import BuilderAgentV3, BuilderPipeline
from .builder_v4 import BuilderV4, BuilderV4Report, DirectOllamaClient, FileResponseParser, GeneratedFile
from .file_writer import BuilderFileWriter
from .generator_v3 import LLMGenerator
from .generator import CodeGenerator
from .generation_validator import GenerationValidationResult, GenerationValidator
from .llm_interface import (
    BaseLLMProvider,
    BuilderLLMClient,
    BuilderLLMResponse,
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    OpenRouterProvider,
)
from .package_validator import PackageValidationResult, PackageValidator
from .pipeline import BuilderExecutionPipeline, BuilderPatchGenerator
from .project_creator_v3 import ProjectCreator
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager
from .provider_factory_v3 import BuilderProviderFactory, ConfiguredLLMProvider, ProviderConfig
from .report_v2 import BuilderV2Report, SelfHealingAction
from .reporter_v3 import BuilderReporter, BuilderV3Report
from .reporter import BuildReport, BuildReporter
from .specification_validator import ExpectedProjectSpecification, SpecificationValidationResult, SpecificationValidator
from .tester import TestOutcome, TestRunner
from .validation_v3 import Compiler, PytestRunner
from .validator import BuildValidator, ValidationResult

__all__ = [
    "BuilderAgent",
    "BuilderAgentV3",
    "BuilderAgentReport",
    "BuilderEngine",
    "BuilderExecutionPipeline",
    "BuilderFileWriter",
    "BuilderLLMClient",
    "BuilderLLMResponse",
    "BuilderPromptManager",
    "BuilderPatchGenerator",
    "BuilderPipeline",
    "BuilderProviderFactory",
    "BuilderReporter",
    "BuilderV2Report",
    "BuilderV3Report",
    "BuilderV4",
    "BuilderV4Report",
    "BaseLLMProvider",
    "CodeGenerator",
    "Compiler",
    "ConfiguredLLMProvider",
    "DirectOllamaClient",
    "FileResponseParser",
    "GeminiProvider",
    "GenerationValidationResult",
    "GenerationValidator",
    "GeneratedFile",
    "GroqProvider",
    "LLMGenerator",
    "OllamaProvider",
    "OpenRouterProvider",
    "PackageValidationResult",
    "PackageValidator",
    "ProjectCreator",
    "ProjectFile",
    "ProjectSpec",
    "ProviderConfig",
    "PytestRunner",
    "ExpectedProjectSpecification",
    "SpecificationValidationResult",
    "SpecificationValidator",
    "BuildValidator",
    "SelfHealingAction",
    "TestRunner",
    "TestOutcome",
    "BuildReporter",
    "BuildReport",
    "ValidationResult",
    "main",
]

__version__ = "1.0.0"
