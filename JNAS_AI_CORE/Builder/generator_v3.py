"""File generation stage for Builder Agent V3."""

from __future__ import annotations

import logging

from .llm_interface import BuilderLLMClient, BuilderLLMResponse
from .project_spec import ProjectFile, ProjectSpec
from .prompt_manager import BuilderPromptManager


class LLMGenerator:
    """Generate one project file at a time."""

    def __init__(
        self,
        llm_client: BuilderLLMClient,
        prompt_manager: BuilderPromptManager | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager or BuilderPromptManager()
        self.logger = logger or logging.getLogger(__name__)

    def generate_file(self, spec: ProjectSpec, project_file: ProjectFile) -> BuilderLLMResponse:
        """Generate one file for a project."""
        self.logger.info("Generate One File Started: %s.", project_file.path)
        prompt = self.prompt_manager.build_file_prompt(spec, project_file)
        response = self.llm_client.generate(prompt)
        self.logger.info("Generate One File Finished: %s.", project_file.path)
        return response
