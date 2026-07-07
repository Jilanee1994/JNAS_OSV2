"""Tests for JNAS Builder Agent V1."""

from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.Builder import BuilderAgent, BuilderFileWriter, ProjectSpec


class FakeLLM:
    """Deterministic LLM test double."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "README.md" in prompt:
            return "# AI File Organizer\n"
        if "requirements.txt" in prompt:
            return "pytest\n"
        if "__init__.py" in prompt:
            return "from .service import FileOrganizer\n\n__all__ = ['FileOrganizer']\n"
        if "config.py" in prompt:
            return "from dataclasses import dataclass\n\n@dataclass\nclass OrganizerConfig:\n    root: str = '.'\n"
        if "models.py" in prompt:
            return "from dataclasses import dataclass\n\n@dataclass\nclass FileRecord:\n    path: str\n    category: str\n"
        if "service.py" in prompt:
            return (
                "class FileOrganizer:\n"
                "    def classify(self, filename: str) -> str:\n"
                "        return filename.rsplit('.', 1)[-1] if '.' in filename else 'unknown'\n"
            )
        if "tests/test_ai_file_organizer.py" in prompt:
            return (
                "from ai_file_organizer.service import FileOrganizer\n\n"
                "def test_classify_extension():\n"
                "    assert FileOrganizer().classify('a.txt') == 'txt'\n"
            )
        return "from .service import FileOrganizer\n\n\ndef main():\n    return FileOrganizer()\n"


class RepairLLM(FakeLLM):
    """LLM that first emits broken code then repairs it."""

    def __init__(self) -> None:
        super().__init__()
        self.broken_sent = False

    def generate(self, prompt: str) -> str:
        if "service.py" in prompt and "Validation errors to fix" not in prompt and not self.broken_sent:
            self.broken_sent = True
            return "class FileOrganizer:\n    def broken(:\n        pass\n"
        if "service.py" in prompt and "validation errors" in prompt:
            return (
                "class FileOrganizer:\n"
                "    def classify(self, filename: str) -> str:\n"
                "        return 'fixed'\n"
            )
        if "tests/test_ai_file_organizer.py" in prompt and "validation errors" in prompt:
            return (
                "from ai_file_organizer.service import FileOrganizer\n\n"
                "def test_classify_extension():\n"
                "    assert FileOrganizer().classify('a.txt') == 'fixed'\n"
            )
        return super().generate(prompt)


def small_spec() -> dict[str, object]:
    return {
        "name": "AI File Organizer",
        "files": [
            {"path": "README.md", "purpose": "readme", "kind": "markdown"},
            {"path": "requirements.txt", "purpose": "dependencies", "kind": "text"},
            {"path": "ai_file_organizer/__init__.py", "purpose": "exports", "kind": "python"},
            {"path": "ai_file_organizer/main.py", "purpose": "entry point", "kind": "python"},
            {"path": "ai_file_organizer/service.py", "purpose": "organizer service", "kind": "python"},
            {"path": "tests/test_ai_file_organizer.py", "purpose": "tests", "kind": "python"},
        ],
    }


def test_project_spec_defaults() -> None:
    spec = ProjectSpec.from_input("AI File Organizer")

    assert spec.slug == "ai_file_organizer"
    assert any(item.path.as_posix() == "ai_file_organizer/service.py" for item in spec.files)


def test_builder_agent_creates_files_and_report(tmp_path: Path) -> None:
    agent = BuilderAgent(llm_manager=FakeLLM(), workspace=tmp_path, retry_limit=1)

    report = agent.build_project(small_spec())

    assert report.success is True
    assert (report.project_root / "ai_file_organizer" / "service.py").exists()
    assert (report.project_root / "tests" / "test_ai_file_organizer.py").exists()
    assert (report.project_root / "BUILD_REPORT.md").exists()
    assert report.compile_result is not None and report.compile_result.success
    assert report.test_result is not None and report.test_result.success


def test_builder_agent_repairs_failed_file(tmp_path: Path) -> None:
    agent = BuilderAgent(llm_manager=RepairLLM(), workspace=tmp_path, retry_limit=2)

    report = agent.build_project(small_spec())
    service_code = (report.project_root / "ai_file_organizer" / "service.py").read_text(encoding="utf-8")

    assert report.success is True
    assert report.retries >= 1
    assert "def classify" in service_code


def test_file_writer_rejects_path_escape(tmp_path: Path) -> None:
    writer = BuilderFileWriter()
    root = tmp_path / "project"
    root.mkdir()

    try:
        writer.write_file(root, Path("../escape.py"), "x = 1")
    except ValueError:
        assert True
    else:
        assert False, "Expected path escape to be rejected."
