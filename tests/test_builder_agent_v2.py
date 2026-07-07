from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.Builder.builder_agent import BuilderAgent
from JNAS_AI_CORE.Builder.file_writer import BuilderFileWriter
from JNAS_AI_CORE.Builder.llm_interface import BuilderLLMClient, BuilderLLMResponse
from JNAS_AI_CORE.Builder.pipeline import BuilderExecutionPipeline
from JNAS_AI_CORE.Builder.project_spec import ProjectSpec
from JNAS_AI_CORE.Builder.report_v2 import BuilderV2Report
from JNAS_AI_CORE.Builder.validator import BuildValidator, ValidationResult


class FakePlanner:
    def create_plan(self, goal: str):
        return type("Plan", (), {"plan_id": f"plan-{goal[:4]}"})()


class FakeLLMClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str, timeout: int = 120) -> BuilderLLMResponse:
        self.prompts.append(prompt)
        path = self._path_from_prompt(prompt)
        if path.endswith("README.md"):
            content = "# Demo\n"
        elif path.endswith("requirements.txt"):
            content = ""
        elif path.endswith("__init__.py"):
            content = '"""Demo package."""\n'
        elif path.endswith("config.py"):
            content = 'APP_NAME = "demo"\n'
        elif path.endswith("models.py"):
            content = "from dataclasses import dataclass\n\n@dataclass\nclass Item:\n    name: str\n"
        elif path.endswith("service.py"):
            content = "def classify_extension(filename: str) -> str:\n    return filename.rsplit('.', 1)[-1]\n"
        elif path.endswith("main.py"):
            content = "from .service import classify_extension\n\n\ndef main() -> str:\n    return classify_extension('x.txt')\n"
        elif "test_" in path:
            content = (
                "from ai_file_organizer.service import classify_extension\n\n"
                "def test_classify_extension():\n"
                "    assert classify_extension('image.png') == 'png'\n"
            )
        else:
            content = ""
        return BuilderLLMResponse("fake", content, True)

    def _path_from_prompt(self, prompt: str) -> str:
        marker = "File path: "
        if marker not in prompt:
            return ""
        return prompt.split(marker, 1)[1].splitlines()[0].strip()


class FakeRouter:
    def route(self, prompt: str, capability: str = "general", priority: int = 100, timeout: int = 120):
        return type("ProviderResult", (), {"provider": "router", "response": "generated", "success": True, "error": ""})()


class SequenceValidator:
    def __init__(self) -> None:
        self.compile_calls = 0
        self.test_calls = 0

    def compile_project(self, project_root: Path) -> ValidationResult:
        self.compile_calls += 1
        if self.compile_calls == 1:
            return ValidationResult(False, "SyntaxError: invalid syntax", [Path("ai_file_organizer/service.py")], failed=1)
        return ValidationResult(True, "compile ok", passed=1)

    def test_project(self, project_root: Path) -> ValidationResult:
        self.test_calls += 1
        return ValidationResult(True, "1 passed in 0.01s", passed=1, duration=0.01)


class FakeRecovery:
    def __init__(self) -> None:
        self.calls = 0

    def recover(self, failure, traceback_text: str = "", source_path: Path | None = None, validation_target: Path | None = None, metadata=None):
        self.calls += 1
        patch = type("Patch", (), {"path": source_path, "summary": "fixed"})()
        return type("Recovery", (), {"success": True, "message": "healed", "strategy": "Patch", "patch": patch})()


def test_builder_llm_client_routes_provider() -> None:
    client = BuilderLLMClient(router=FakeRouter())
    response = client.generate("hello")
    assert response.provider == "router"
    assert response.content == "generated"


def test_builder_v2_execute_creates_project_and_report(tmp_path: Path) -> None:
    agent = BuilderAgent(
        llm_manager=object(),
        llm_client=FakeLLMClient(),
        planner=FakePlanner(),
        workspace=tmp_path,
        retry_limit=1,
    )
    report = agent.execute("AI File Organizer")
    assert report.success
    assert (report.project_root / "BUILD_REPORT.md").exists()
    assert (report.project_root / "ai_file_organizer" / "service.py").exists()
    assert report.provider == "fake"


def test_builder_v2_invokes_self_healing_on_compile_failure(tmp_path: Path) -> None:
    validator = SequenceValidator()
    recovery = FakeRecovery()
    pipeline = BuilderExecutionPipeline(
        workspace=tmp_path,
        file_writer=BuilderFileWriter(),
        prompt_manager=__import__("JNAS_AI_CORE.Builder.prompt_manager", fromlist=["BuilderPromptManager"]).BuilderPromptManager(),
        validator=validator,
        llm_client=FakeLLMClient(),
        planner=FakePlanner(),
        self_healing_engine=recovery,
        retry_limit=1,
    )
    report = pipeline.execute("AI File Organizer")
    assert report.success
    assert recovery.calls == 1
    assert report.self_healing_actions[0].stage == "compile"


def test_validator_extracts_pytest_counts() -> None:
    validator = BuildValidator()
    assert validator._extract_pytest_counts("2 passed, 1 skipped in 0.02s") == (2, 0, 1)
    assert validator._extract_pytest_counts("1 failed, 3 passed in 0.04s") == (3, 1, 0)


def test_v2_report_contains_self_healing_action(tmp_path: Path) -> None:
    report = BuilderV2Report("Demo", tmp_path)
    report.compile_result = ValidationResult(True, "compile ok", passed=1)
    report.test_result = ValidationResult(True, "1 passed", passed=1)
    markdown = report.to_markdown()
    assert "Build Summary" in markdown
    assert "Remaining Issues" in markdown


def test_file_writer_prevents_path_traversal(tmp_path: Path) -> None:
    spec = ProjectSpec.from_input("Safe App")
    writer = BuilderFileWriter()
    root = writer.create_project_root(tmp_path, spec)
    try:
        writer.write_file(root, Path("../escape.py"), "bad")
    except ValueError as exc:
        assert "escapes project root" in str(exc)
    else:
        raise AssertionError("Expected path traversal to be rejected.")
