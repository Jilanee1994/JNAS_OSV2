"""Autonomous code generation worker backed by the Ollama HTTP API."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.configuration import ConfigManager
    from JNAS_AI_CORE.registry.metadata import ToolMetadata
except ImportError:
    ConfigManager = None
    ToolMetadata = None

from .build_validator import BuildValidationResult, BuildValidator
from .file_writer import GeneratedFileWriter
from .generation_history import GenerationHistory, GenerationHistoryEntry
from .llm_client import OllamaApiClient
from .prompt_manager import PromptManager
from .retry_manager import RetryManager


@dataclass(frozen=True)
class CodeGenerationResult:
    """Result returned by the autonomous code generation worker."""

    success: bool
    target_root: Path
    generated_files: list[Path] = field(default_factory=list)
    retries: int = 0
    compile_output: str = ""
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0


class CodeGenerationWorker:
    """Generate, write, validate, and automatically repair code with Ollama."""

    name = "code_generation"

    def __init__(
        self,
        llm_client: OllamaApiClient | None = None,
        prompt_manager: PromptManager | None = None,
        file_writer: GeneratedFileWriter | None = None,
        build_validator: BuildValidator | None = None,
        retry_manager: RetryManager | None = None,
        history: GenerationHistory | None = None,
        config_manager: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config_manager = config_manager or (ConfigManager() if ConfigManager is not None else None)
        self.logger = logger or logging.getLogger("JNAS_AI_CORE.workers.code_generation")
        self.llm_client = llm_client or OllamaApiClient(
            host=str(self._config_get("code_generation.ollama_host", "http://127.0.0.1:11434")),
            model=str(self._config_get("code_generation.model", "qwen2.5:7b")),
            timeout=int(self._config_get("code_generation.timeout", 300)),
            logger=self.logger,
        )
        self.prompt_manager = prompt_manager or PromptManager()
        self.file_writer = file_writer or GeneratedFileWriter()
        self.build_validator = build_validator or BuildValidator()
        self.retry_manager = retry_manager or RetryManager(
            max_retries=int(self._config_get("code_generation.max_retries", 3))
        )
        self.history = history or GenerationHistory()
        self.metadata = self._build_metadata()

    def initialize(self) -> None:
        """Prepare the worker for registry use."""
        self.logger.info("CodeGenerationWorker initialized.")

    def validate(self) -> bool:
        """Validate worker readiness."""
        return all([self.llm_client, self.prompt_manager, self.file_writer, self.build_validator])

    def shutdown(self) -> None:
        """Release worker resources."""
        self.logger.info("CodeGenerationWorker shutdown complete.")

    def execute(self, payload: Any, context: Any | None = None) -> CodeGenerationResult:
        """Execute generation from a task, payload dictionary, or plain instruction."""
        request = self._normalize_payload(payload, context)
        return self.generate_project(
            instruction=request["instruction"],
            target_root=request["target_root"],
            project_context=request["project_context"],
        )

    def generate_project(
        self,
        instruction: str,
        target_root: Path,
        project_context: str = "",
    ) -> CodeGenerationResult:
        """Generate files and retry with compiler feedback until validation succeeds."""
        started = time.perf_counter()
        prompt = self.prompt_manager.build_generation_prompt(
            instruction=instruction,
            project_context=project_context,
            target_root=str(target_root),
        )
        history_entry = GenerationHistoryEntry(prompt=prompt)
        errors: list[str] = []
        generated_paths: list[Path] = []
        compile_result = BuildValidationResult(False, "", 1)
        current_prompt = prompt
        retries = 0

        while True:
            self.logger.info("Requesting code generation attempt %s.", retries + 1)
            response = self.llm_client.generate(current_prompt)
            generated_files = self.file_writer.extract_files(response)
            generated_paths = self.file_writer.write_files(generated_files, target_root)
            history_entry.generated_files = [str(path) for path in generated_paths]
            compile_result = self.build_validator.validate(target_root)
            if compile_result.success:
                history_entry.final_status = "success"
                break

            errors.append(compile_result.output)
            history_entry.compile_errors.append(compile_result.output)
            if not self.retry_manager.can_retry(retries):
                history_entry.final_status = "failed"
                break
            retries += 1
            current_prompt = self.prompt_manager.build_fix_prompt(
                original_prompt=prompt,
                compiler_output=compile_result.output,
                previous_files=[str(path) for path in generated_paths],
            )

        duration = time.perf_counter() - started
        history_entry.retries = retries
        history_entry.duration = duration
        self.history.add(history_entry)
        return CodeGenerationResult(
            success=compile_result.success,
            target_root=target_root,
            generated_files=generated_paths,
            retries=retries,
            compile_output=compile_result.output,
            errors=errors,
            duration=duration,
        )

    def _normalize_payload(self, payload: Any, context: Any | None) -> dict[str, Any]:
        if isinstance(payload, dict):
            instruction = str(payload.get("instruction") or payload.get("prompt") or payload.get("description") or "")
            target_root = Path(str(payload.get("target_root", self._config_get("code_generation.output_dir", "JNAS_AI_CORE/workspace/generated"))))
            project_context = str(payload.get("project_context", ""))
            return {"instruction": instruction, "target_root": target_root, "project_context": project_context}

        description = getattr(payload, "description", None)
        title = getattr(payload, "title", "")
        instruction = str(description or title or payload)
        metadata = getattr(payload, "metadata", {}) or {}
        target_root = Path(str(metadata.get("target_root", self._config_get("code_generation.output_dir", "JNAS_AI_CORE/workspace/generated"))))
        project_context = str(metadata.get("project_context", ""))
        return {"instruction": instruction, "target_root": target_root, "project_context": project_context}

    def _config_get(self, dotted_key: str, default: Any = None) -> Any:
        if self.config_manager is None:
            return default
        return self.config_manager.get(dotted_key, default)

    def _build_metadata(self) -> Any:
        if ToolMetadata is None:
            return None
        return ToolMetadata(
            tool_id="code_generation_worker",
            name="Autonomous Code Generation Worker",
            description="Generates, writes, compiles, and repairs Python code through the Ollama HTTP API.",
            version="1.0.0",
            author="JNAS_AI_CORE",
            category="code",
            supported_tasks=["code_generation", "builder", "automation"],
            input_types=["dict", "Task", "str"],
            output_types=["CodeGenerationResult"],
            enabled=True,
            priority=10,
        )
