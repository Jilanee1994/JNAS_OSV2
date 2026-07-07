"""Generated content validation for Builder Agent."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

from .project_spec import ProjectFile, ProjectSpec


@dataclass(frozen=True)
class GenerationValidationResult:
    """Result of validating one generated file."""

    success: bool
    file_path: Path
    errors: list[str] = field(default_factory=list)

    def to_message(self) -> str:
        """Render validation errors for corrective prompts."""
        if self.success:
            return "Generation validation passed."
        return "\n".join(f"- {error}" for error in self.errors)


class GenerationValidator:
    """Reject low-quality or structurally invalid generated content."""

    _PLACEHOLDER_PATTERNS = (
        re.compile(r"\byour_module\b", re.IGNORECASE),
        re.compile(r"\byour_package\b", re.IGNORECASE),
        re.compile(r"\bpackage_name\b", re.IGNORECASE),
        re.compile(r"\bmodule_name\b", re.IGNORECASE),
        re.compile(r"\bTODO\b", re.IGNORECASE),
        re.compile(r"\bFIXME\b", re.IGNORECASE),
        re.compile(r"\bplaceholder\b", re.IGNORECASE),
        re.compile(r"\bexample\b", re.IGNORECASE),
        re.compile(r"NotImplementedError"),
        re.compile(r"^\s*pass\s*(?:#.*)?$", re.MULTILINE),
        re.compile(r"={3,}\s*FILE:", re.IGNORECASE),
    )
    _FAKE_IMPORTS = (
        re.compile(r"^\s*(?:from|import)\s+your_", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*from\s+(?:module|package|example)", re.IGNORECASE | re.MULTILINE),
    )

    def validate(self, spec: ProjectSpec, project_file: ProjectFile, content: str) -> GenerationValidationResult:
        """Validate generated content before it is written to disk."""
        errors: list[str] = []
        is_python = project_file.kind == "python" or project_file.path.suffix == ".py"
        if (not content or not content.strip()) and project_file.path.name != "requirements.txt":
            errors.append("Generated content is empty.")
        if is_python:
            errors.extend(self._placeholder_errors(content))
            errors.extend(self._fake_import_errors(content))
            errors.extend(self._python_structure_errors(spec, project_file, content))
        return GenerationValidationResult(not errors, project_file.path, errors)

    def _placeholder_errors(self, content: str) -> list[str]:
        errors = []
        for pattern in self._PLACEHOLDER_PATTERNS:
            if pattern.search(content):
                errors.append(f"Placeholder or incomplete code detected: {pattern.pattern}")
        return errors

    def _fake_import_errors(self, content: str) -> list[str]:
        return [f"Fake import detected: {pattern.pattern}" for pattern in self._FAKE_IMPORTS if pattern.search(content)]

    def _python_structure_errors(self, spec: ProjectSpec, project_file: ProjectFile, content: str) -> list[str]:
        path = project_file.path
        errors: list[str] = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        functions = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        if path.name == "__init__.py":
            return errors
        if path.parts and path.parts[0] == "tests":
            if not any(name.startswith("test_") for name in functions):
                errors.append("Test file must define at least one pytest test function.")
            return errors
        if not functions and not classes:
            errors.append("Python implementation must define at least one function or class.")
        expected_function = self._expected_function_name(path)
        if expected_function and expected_function not in functions and not classes:
            errors.append(f"Missing required function or class for requested file: {expected_function}")
        if path.stem == "hello" and "hello" in spec.description.lower() and "hello" not in functions:
            errors.append("Hello project requires a hello() function in hello.py.")
        return errors

    def _expected_function_name(self, path: Path) -> str:
        if path.stem in {"main", "config", "models", "service", "app"}:
            return ""
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", path.stem):
            return ""
        return path.stem
