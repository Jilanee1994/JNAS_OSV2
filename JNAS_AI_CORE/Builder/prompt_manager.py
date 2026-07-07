"""Prompt management for Builder Agent V1."""

from __future__ import annotations

from .project_spec import ProjectFile, ProjectSpec
from .specification_validator import SpecificationValidator


class BuilderPromptManager:
    """Build file-by-file prompts and repair prompts for Ollama."""

    def __init__(self, specification_validator: SpecificationValidator | None = None) -> None:
        self.specification_validator = specification_validator or SpecificationValidator()

    def build_file_prompt(self, spec: ProjectSpec, project_file: ProjectFile) -> str:
        """Create a prompt for a single project file."""
        return (
            "You are the autonomous JNAS Builder Agent.\n"
            "Generate exactly one file for a software project.\n"
            "Never ask for confirmation.\n"
            "Do not ask to continue.\n"
            "Return only the raw file content.\n"
            "Do not include markdown fences, filename markers, or explanations.\n\n"
            "Never output placeholder code.\n"
            "Never use your_module, your_package, package_name, TODO, FIXME, placeholder, or example code.\n"
            "Never use pass as a final implementation.\n"
            "Never raise NotImplementedError.\n"
            "Output production-ready executable Python only for Python files.\n\n"
            f"{self._specification_text(spec)}"
            f"Project name: {spec.name}\n"
            f"Project slug: {spec.slug}\n"
            f"Project description: {spec.description}\n"
            f"File path: {project_file.path.as_posix()}\n"
            f"File purpose: {project_file.purpose}\n"
            f"File kind: {project_file.kind}\n\n"
            "Use Python 3.12, type hints, docstrings, and simple maintainable design for Python files.\n"
            "For tests, use pytest and avoid external services.\n"
            f"When importing generated package code, use absolute imports from `{spec.slug}`.\n"
            "For Hello World projects, implement greet() in hello.py and test it with "
            f"`from {spec.slug}.hello import greet`.\n"
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
            "Never output placeholder code, TODO, FIXME, pass-only implementation, fake imports, or NotImplementedError.\n"
            "The corrected file must be executable production-ready Python when the file kind is Python.\n\n"
            f"Project name: {spec.name}\n"
            f"Project slug: {spec.slug}\n"
            f"File path: {project_file.path.as_posix()}\n"
            f"File purpose: {project_file.purpose}\n\n"
            f"Tests must import generated package modules from `{spec.slug}`.\n"
            "Only use these validation errors to produce the corrected file:\n"
            f"{errors}\n"
        )

    def build_generation_correction_prompt(
        self,
        spec: ProjectSpec,
        project_file: ProjectFile,
        invalid_content: str,
        validation_errors: str,
    ) -> str:
        """Create a prompt for regenerating one rejected file before writing."""
        _ = invalid_content
        return (
            "You violated the Builder output quality rules.\n"
            "Regenerate ONLY the requested file.\n"
            "Return only complete raw file content.\n"
            "Do not include explanations, markdown fences, or filename markers.\n\n"
            "Forbidden output:\n"
            "- your_module\n"
            "- TODO\n"
            "- FIXME\n"
            "- placeholder\n"
            "- example code\n"
            "- pass as final implementation\n"
            "- NotImplementedError\n"
            "- fake imports\n\n"
            f"{self._specification_text(spec)}"
            f"Project name: {spec.name}\n"
            f"Project slug: {spec.slug}\n"
            f"File path: {project_file.path.as_posix()}\n"
            f"File purpose: {project_file.purpose}\n\n"
            f"Tests must import generated package modules from `{spec.slug}`.\n"
            "Validation errors:\n"
            f"{validation_errors}\n"
        )

    def _specification_text(self, spec: ProjectSpec) -> str:
        expected = self.specification_validator.expected_from_prompt(spec.description)
        if expected is None:
            return ""
        forbidden = expected.format_forbidden_files()
        return (
            "Generate EXACTLY these files for this project:\n"
            f"{expected.format_required_files()}\n\n"
            "Do NOT generate these files:\n"
            f"{forbidden or 'none'}\n\n"
            "Output only the requested current file.\n\n"
        )
