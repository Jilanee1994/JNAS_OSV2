"""File generation stage for Builder Agent V3."""

from __future__ import annotations

import logging

from .llm_interface import BuilderLLMClient, BuilderLLMResponse
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager
from .generation_validator import GenerationValidator


class LLMGenerator:
    """Generate one project file at a time."""

    def __init__(
        self,
        llm_client: BuilderLLMClient,
        prompt_manager: BuilderPromptManager | None = None,
        generation_validator: GenerationValidator | None = None,
        max_retries: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager or BuilderPromptManager()
        self.generation_validator = generation_validator or GenerationValidator()
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

    def generate_file(self, spec: ProjectSpec, project_file: ProjectFile) -> BuilderLLMResponse:
        """Generate one file for a project."""
        self.logger.info("Generate One File Started: %s.", project_file.path)
        prompt = self.prompt_manager.build_file_prompt(spec, project_file)
        response = self._generate_validated(spec, project_file, prompt)
        self.logger.info("Generate One File Finished: %s.", project_file.path)
        return response

    def _generate_validated(self, spec: ProjectSpec, project_file: ProjectFile, prompt: str) -> BuilderLLMResponse:
        current_prompt = prompt
        last_errors = ""
        for attempt in range(self.max_retries + 1):
            response = self.llm_client.generate(current_prompt)
            result = self.generation_validator.validate(spec, project_file, response.content)
            if result.success:
                return response
            last_errors = result.to_message()
            self.logger.warning("Generated file rejected: %s. Attempt %s.", project_file.path, attempt + 1)
            if attempt >= self.max_retries:
                break
            current_prompt = self.prompt_manager.build_generation_correction_prompt(
                spec,
                project_file,
                response.content,
                last_errors,
            )
        raise ValueError(f"Generated content failed validation for {project_file.path}:\n{last_errors}")
