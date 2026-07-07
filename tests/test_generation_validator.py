from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.Builder import BuilderAgent, GenerationValidator, ProjectFile, ProjectSpec, SpecificationValidator


class PlaceholderThenValidLLM:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        requested_path = self._requested_path(prompt)
        if requested_path == "tests/test_hello.py":
            return "from hello import hello\n\n\ndef test_hello():\n    assert hello() == 'Hello, World!'\n"
        if self.calls == 1:
            return "from your_module import thing\n\nTODO = True\n\ndef hello():\n    pass\n"
        return "def hello() -> str:\n    return 'Hello, World!'\n"

    def _requested_path(self, prompt: str) -> str:
        marker = "File path: "
        return prompt.split(marker, 1)[1].splitlines()[0].strip() if marker in prompt else ""


def hello_spec() -> ProjectSpec:
    return ProjectSpec(
        name="Hello World",
        slug="hello_world",
        description="Create a Hello World Python project with one file named hello.py",
        files=[
            ProjectFile(Path("hello.py"), "Hello implementation.", "python"),
            ProjectFile(Path("tests") / "test_hello.py", "Hello tests.", "python"),
        ],
    )


def test_generation_validator_rejects_placeholder_code() -> None:
    result = GenerationValidator().validate(
        hello_spec(),
        ProjectFile(Path("hello.py"), "Hello implementation.", "python"),
        "from your_module import thing\n\n# TODO\n\ndef hello():\n    pass\n",
    )
    assert not result.success
    assert any("Placeholder" in error or "Fake import" in error for error in result.errors)


def test_generation_validator_accepts_production_code() -> None:
    result = GenerationValidator().validate(
        hello_spec(),
        ProjectFile(Path("hello.py"), "Hello implementation.", "python"),
        "def hello() -> str:\n    return 'Hello, World!'\n",
    )
    assert result.success


def test_specification_validator_detects_missing_and_unexpected_files() -> None:
    expected = SpecificationValidator().expected_from_prompt(
        "Create a Hello World Python project with one file named hello.py"
    )
    assert expected is not None
    result = expected.validate([Path("main.py"), Path("service.py")])
    assert not result.success
    assert Path("hello.py") in result.missing_files
    assert Path("main.py") in result.unexpected_files


def test_builder_agent_retries_invalid_generation_before_write(tmp_path: Path) -> None:
    llm = PlaceholderThenValidLLM()
    agent = BuilderAgent(llm_manager=llm, workspace=tmp_path, retry_limit=3)
    report = agent.build_project("Create a Hello World Python project with one file named hello.py")

    assert report.success
    assert report.retries >= 1
    assert (report.project_root / "hello.py").exists()
    assert (report.project_root / "tests" / "test_hello.py").exists()
    assert not (report.project_root / "main.py").exists()
    assert not (report.project_root / "service.py").exists()
    assert "your_module" not in (report.project_root / "hello.py").read_text(encoding="utf-8")
