"""Project specification enforcement for Builder Agent V3.1."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .project_spec import ProjectFile, ProjectSpec


@dataclass(frozen=True)
class SpecificationValidationResult:
    """Result of validating generated files against an expected specification."""

    success: bool
    expected_files: set[Path]
    generated_files: set[Path]
    missing_files: set[Path] = field(default_factory=set)
    unexpected_files: set[Path] = field(default_factory=set)
    forbidden_files: set[Path] = field(default_factory=set)

    def to_message(self) -> str:
        """Render validation details for corrective prompts and reports."""
        lines = [
            f"Expected: {', '.join(path.as_posix() for path in sorted(self.expected_files)) or 'none'}",
            f"Generated: {', '.join(path.as_posix() for path in sorted(self.generated_files)) or 'none'}",
        ]
        if self.missing_files:
            lines.append(f"Missing: {', '.join(path.as_posix() for path in sorted(self.missing_files))}")
        if self.unexpected_files:
            lines.append(f"Unexpected: {', '.join(path.as_posix() for path in sorted(self.unexpected_files))}")
        if self.forbidden_files:
            lines.append(f"Forbidden: {', '.join(path.as_posix() for path in sorted(self.forbidden_files))}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ExpectedProjectSpecification:
    """Expected file contract for one Builder run."""

    name: str
    slug: str
    description: str
    required_files: set[Path]
    optional_files: set[Path] = field(default_factory=set)
    forbidden_files: set[Path] = field(default_factory=set)

    @property
    def allowed_files(self) -> set[Path]:
        """Return all files the builder may generate before reports."""
        return set(self.required_files) | set(self.optional_files)

    def to_project_spec(self) -> ProjectSpec:
        """Convert the expected specification into a Builder ProjectSpec."""
        files = [
            ProjectFile(path, self._purpose_for(path), self._kind_for(path))
            for path in sorted(self.required_files)
        ]
        files.extend(
            ProjectFile(path, self._purpose_for(path), self._kind_for(path))
            for path in sorted(self.optional_files)
        )
        return ProjectSpec(self.name, self.slug, self.description, files)

    def validate(self, generated_files: Iterable[Path]) -> SpecificationValidationResult:
        """Validate generated paths before accepting or writing files."""
        generated = {_normalize(path) for path in generated_files}
        expected = self.allowed_files
        missing = set(self.required_files) - generated
        unexpected = generated - expected
        forbidden = generated & self.forbidden_files
        return SpecificationValidationResult(
            success=not missing and not unexpected and not forbidden,
            expected_files=expected,
            generated_files=generated,
            missing_files=missing,
            unexpected_files=unexpected,
            forbidden_files=forbidden,
        )

    def corrective_prompt(self, generated_files: Iterable[Path]) -> str:
        """Build a corrective prompt for specification violations."""
        result = self.validate(generated_files)
        return (
            "You violated the project specification.\n\n"
            f"{result.to_message()}\n\n"
            "Generate ONLY these files:\n"
            f"{self.format_required_files()}\n"
        )

    def format_required_files(self) -> str:
        """Render required files for prompts."""
        return "\n".join(path.as_posix() for path in sorted(self.required_files))

    def format_forbidden_files(self) -> str:
        """Render forbidden files for prompts."""
        return "\n".join(path.as_posix() for path in sorted(self.forbidden_files))

    def _purpose_for(self, path: Path) -> str:
        if path.name.startswith("test_"):
            return f"Pytest coverage for {path.stem.removeprefix('test_')}.py."
        if path.suffix == ".py":
            return f"Implementation for {path.name}."
        if path.name == "requirements.txt":
            return "Project dependencies."
        if path.name == "README.md":
            return "Project overview."
        return f"Generated project file {path.as_posix()}."

    def _kind_for(self, path: Path) -> str:
        if path.suffix == ".py":
            return "python"
        if path.suffix == ".md":
            return "markdown"
        return "text"


class SpecificationValidator:
    """Parse and enforce expected Builder project specifications."""

    _EXPLICIT_FILE_PATTERN = re.compile(
        r"(?:file|named|called)\s+(?:named\s+|called\s+)?[`'\"]?([A-Za-z0-9_./-]+\.py)[`'\"]?",
        re.IGNORECASE,
    )
    _DEFAULT_FORBIDDEN = {
        Path("main.py"),
        Path("service.py"),
        Path("models.py"),
        Path("config.py"),
        Path("app.py"),
    }

    def expected_from_prompt(self, prompt: str) -> ExpectedProjectSpecification | None:
        """Infer a strict expected specification from an explicit user prompt."""
        files = self._explicit_python_files(prompt)
        if not files:
            return None
        required = set(files)
        for file_path in files:
            required.add(Path("tests") / f"test_{file_path.stem}.py")
        forbidden = {path for path in self._DEFAULT_FORBIDDEN if path not in required}
        name = self._name_from_prompt(prompt, files[0])
        slug = self._slug_from_name(name)
        return ExpectedProjectSpecification(
            name=name,
            slug=slug,
            description=prompt,
            required_files=required,
            forbidden_files=forbidden,
        )

    def validate_project_spec(
        self,
        expected: ExpectedProjectSpecification,
        spec: ProjectSpec,
    ) -> SpecificationValidationResult:
        """Validate a ProjectSpec against the expected file contract."""
        return expected.validate(item.path for item in spec.files)

    def _explicit_python_files(self, prompt: str) -> list[Path]:
        found = []
        for match in self._EXPLICIT_FILE_PATTERN.findall(prompt):
            path = _normalize(Path(match))
            if path.name.startswith("test_") or path.parts[0] == "tests":
                continue
            if path not in found:
                found.append(path)
        return found

    def _name_from_prompt(self, prompt: str, file_path: Path) -> str:
        if "hello" in prompt.lower():
            return "Hello World"
        return file_path.stem.replace("_", " ").title()

    def _slug_from_name(self, name: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
        return slug or "jnas_project"


def _normalize(path: Path) -> Path:
    return Path(path.as_posix().lstrip("/\\"))
