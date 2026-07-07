"""Project specification models for Builder Agent V1."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectFile:
    """A file that must be generated for a project."""

    path: Path
    purpose: str
    kind: str = "python"


@dataclass(frozen=True)
class ProjectSpec:
    """Normalized project specification consumed by BuilderAgent."""

    name: str
    slug: str
    description: str
    files: list[ProjectFile] = field(default_factory=list)

    @classmethod
    def from_input(cls, specification: str | dict[str, Any]) -> "ProjectSpec":
        """Create a project specification from text or structured data."""
        if isinstance(specification, dict):
            name = str(specification.get("name", "JNAS Project")).strip()
            description = str(specification.get("description", name)).strip()
            slug = _slugify(str(specification.get("slug", name)))
            files = [
                ProjectFile(
                    path=Path(str(item["path"])),
                    purpose=str(item.get("purpose", item["path"])),
                    kind=str(item.get("kind", "python")),
                )
                for item in specification.get("files", [])
            ]
            return cls(name=name, slug=slug, description=description, files=files or default_files(slug))

        name = specification.strip()
        slug = _slugify(name)
        return cls(name=name, slug=slug, description=name, files=default_files(slug))


def default_files(project_slug: str) -> list[ProjectFile]:
    """Return a production-oriented default Python project layout."""
    package = project_slug.replace("-", "_")
    return [
        ProjectFile(Path("README.md"), "Project overview, usage, and generated file summary.", "markdown"),
        ProjectFile(Path("requirements.txt"), "Runtime and test dependencies.", "text"),
        ProjectFile(Path(package) / "__init__.py", "Package exports.", "python"),
        ProjectFile(Path(package) / "main.py", "Application entry point and primary orchestration.", "python"),
        ProjectFile(Path(package) / "config.py", "Configuration dataclasses and defaults.", "python"),
        ProjectFile(Path(package) / "models.py", "Core project data models.", "python"),
        ProjectFile(Path(package) / "service.py", "Main business service implementation.", "python"),
        ProjectFile(Path("tests") / f"test_{package}.py", "Pytest coverage for the generated package.", "python"),
    ]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "jnas_project"
