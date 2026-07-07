"""Prompt management for Builder Agent V1."""

from __future__ import annotations

from .project_spec import ProjectFile, ProjectSpec


class BuilderPromptManager:
    """Build file-by-file prompts and repair prompts for Ollama."""

    def build_file_prompt(self, spec: ProjectSpec, project_file: ProjectFile) -> str:
        """Create a prompt for a single project file."""
        return (
            "You are the autonomous JNAS Builder Agent.\n"
            "Generate exactly one file for a software project.\n"
            "Never ask for confirmation.\n"
            "Do not ask to continue.\n"
            "Return only the raw file content.\n"
            "Do not include markdown fences, filename markers, or explanations.\n\n"
            f"Project name: {spec.name}\n"
            f"Project slug: {spec.slug}\n"
            f"Project description: {spec.description}\n"
            f"File path: {project_file.path.as_posix()}\n"
            f"File purpose: {project_file.purpose}\n"
            f"File kind: {project_file.kind}\n\n"
            "Use Python 3.12, type hints, docstrings, and simple maintainable design for Python files.\n"
            "For tests, use pytest and avoid external services.\n"
        )

    def build_repair_prompt(
        self,
        spec: ProjectSpec,
        project_file: ProjectFile,
        current_content: str,
        errors: str,
    ) -> str:
        """Create a prompt that repairs exactly one failed file."""
        _ = current_content
        return (
            "You are repairing one generated file for the JNAS Builder Agent.\n"
            "Return only the complete corrected file content.\n"
            "Do not include markdown fences or explanations.\n"
            "Regenerate only the file named below.\n\n"
            f"Project name: {spec.name}\n"
            f"File path: {project_file.path.as_posix()}\n"
            f"File purpose: {project_file.purpose}\n\n"
            "Only use these validation errors to produce the corrected file:\n"
            f"{errors}\n"
        )
