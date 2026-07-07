from __future__ import annotations

import json
from pathlib import Path

from JNAS_AI_CORE.Builder.builder_v3 import BuilderAgentV3, BuilderPipeline
from JNAS_AI_CORE.Builder.llm_interface import BuilderLLMResponse
from JNAS_AI_CORE.Builder.project_creator_v3 import ProjectCreator
from JNAS_AI_CORE.Builder.provider_factory_v3 import BuilderProviderFactory, ConfiguredLLMProvider, ProviderConfig
from JNAS_AI_CORE.Builder.reporter_v3 import BuilderReporter, BuilderV3Report
from JNAS_AI_CORE.Builder.validation_v3 import Compiler, PytestRunner
from JNAS_AI_CORE.Builder.validator import ValidationResult


class FakeConfig:
    def __init__(self) -> None:
        self.values = {
            "builder_v3.provider_priority": ["ollama", "gemini", "groq", "openrouter"],
            "builder_v3.providers": [
                {
                    "name": "groq",
                    "endpoint": "https://groq.test",
                    "model": "groq-model",
                    "provider_type": "groq",
                    "enabled": True,
                },
                {
                    "name": "ollama",
                    "endpoint": "http://127.0.0.1:11434/api/generate",
                    "model": "qwen",
                    "provider_type": "ollama",
                    "enabled": True,
                },
            ],
        }

    def get(self, key: str, default=None):
        return self.values.get(key, default)


class FakePlanner:
    def create_plan(self, goal: str):
        return type("Plan", (), {"plan_id": "plan-v3", "goal": goal})()


class FakeLLMClient:
    def __init__(self, broken_first: bool = False) -> None:
        self.prompts: list[str] = []
        self.broken_first = broken_first
        self.hello_generations = 0

    def generate(self, prompt: str, timeout: int = 120) -> BuilderLLMResponse:
        self.prompts.append(prompt)
        if "Create a compact JSON project specification" in prompt:
            return BuilderLLMResponse("fake-provider", json.dumps(self._spec()), True)
        path = self._path(prompt).replace("\\", "/")
        if path == "README.md":
            return BuilderLLMResponse("fake-provider", "# Hello Project\n", True)
        if path == "requirements.txt":
            return BuilderLLMResponse("fake-provider", "", True)
        if path == "pyproject.toml":
            return BuilderLLMResponse("fake-provider", "[project]\nname = \"hello-project\"\nversion = \"0.1.0\"\n", True)
        if path.endswith("test_hello.py"):
            return BuilderLLMResponse("fake-provider", "from hello_project.hello import greet\n\n\ndef test_greet():\n    assert greet() == 'hello'\n", True)
        if path.endswith("hello.py"):
            self.hello_generations += 1
            if self.broken_first and self.hello_generations == 1:
                return BuilderLLMResponse("fake-provider", "def greet(:\n    return 'hello'\n", True)
            return BuilderLLMResponse("fake-provider", "def greet() -> str:\n    return 'hello'\n", True)
        return BuilderLLMResponse("fake-provider", "", True)

    def _spec(self) -> dict[str, object]:
        return {
            "name": "Hello Project",
            "slug": "hello_project",
            "description": "Build Hello Project",
            "files": [
                {"path": "README.md", "purpose": "Overview", "kind": "markdown"},
                {"path": "requirements.txt", "purpose": "Dependencies", "kind": "text"},
                {"path": "hello_project/hello.py", "purpose": "Hello implementation", "kind": "python"},
                {"path": "tests/test_hello.py", "purpose": "Hello tests", "kind": "python"},
            ],
        }

    def _path(self, prompt: str) -> str:
        marker = "File path: "
        return prompt.split(marker, 1)[1].splitlines()[0].strip() if marker in prompt else ""


class FakeRecovery:
    def __init__(self, replacement: str) -> None:
        self.calls = 0
        self.replacement = replacement

    def recover(self, failure, traceback_text: str = "", source_path: Path | None = None, validation_target: Path | None = None, metadata=None):
        self.calls += 1
        if source_path is not None:
            source_path.write_text(self.replacement, encoding="utf-8")
        patch = type("Patch", (), {"path": source_path, "summary": "rewrote failed file"})()
        return type("Recovery", (), {"success": True, "message": "healed", "strategy": "Patch", "patch": patch})()


class FakeCompiler:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, project_root: Path) -> ValidationResult:
        self.calls += 1
        if self.calls == 1:
            return ValidationResult(False, "SyntaxError", [Path("hello.py")], failed=1, traceback="SyntaxError")
        return ValidationResult(True, "compile ok", passed=1)


class FakePytest:
    def run(self, project_root: Path) -> ValidationResult:
        return ValidationResult(True, "1 passed in 0.01s", passed=1, duration=0.01)


def test_provider_factory_uses_configured_priority() -> None:
    providers = BuilderProviderFactory(config_manager=FakeConfig()).create_providers()
    assert [provider.name for provider in providers] == ["ollama", "groq"]


def test_configured_provider_payloads() -> None:
    ollama = ConfiguredLLMProvider(ProviderConfig("ollama", "http://local", "qwen", "ollama"))
    groq = ConfiguredLLMProvider(ProviderConfig("groq", "http://groq", "llama", "groq"))
    gemini = ConfiguredLLMProvider(ProviderConfig("gemini", "http://gemini", "gemini-pro", "gemini"))
    assert "prompt" in ollama._payload("hello")
    assert "messages" in groq._payload("hello")
    assert "contents" in gemini._payload("hello")


def test_project_creator_generates_spec_from_llm() -> None:
    creator = ProjectCreator(FakeLLMClient(), planner=FakePlanner())
    spec, plan_id = creator.create("Build Hello Project")
    assert plan_id == "plan-v3"
    assert spec.name == "Hello Project"
    assert Path("hello_project") / "hello.py" in [item.path for item in spec.files]


def test_builder_pipeline_builds_hello_project(tmp_path: Path) -> None:
    llm = FakeLLMClient()
    pipeline = BuilderPipeline(
        workspace=tmp_path,
        project_creator=ProjectCreator(llm, planner=FakePlanner()),
        llm_client=llm,
    )
    report = pipeline.run("Build Hello Project")
    assert report.final_result == "SUCCESS"
    assert (report.project_root / "hello_project" / "hello.py").exists()
    assert (report.project_root / "BUILD_REPORT.md").exists()
    assert report.provider_used == "fake-provider"


def test_builder_pipeline_invokes_self_healing(tmp_path: Path) -> None:
    llm = FakeLLMClient()
    recovery = FakeRecovery("def greet() -> str:\n    return 'hello'\n")
    pipeline = BuilderPipeline(
        workspace=tmp_path,
        project_creator=ProjectCreator(llm, planner=FakePlanner()),
        llm_client=llm,
        compiler=FakeCompiler(),
        pytest_runner=FakePytest(),
        self_healing_engine=recovery,
        max_retries=2,
    )
    report = pipeline.run("Build Hello Project")
    assert report.final_result == "SUCCESS"
    assert report.retries == 1
    assert recovery.calls == 1
    assert report.self_healing_actions[0].stage == "compile"


def test_builder_agent_v3_facade_uses_pipeline(tmp_path: Path) -> None:
    pipeline = BuilderPipeline(
        workspace=tmp_path,
        project_creator=ProjectCreator(FakeLLMClient(), planner=FakePlanner()),
        llm_client=FakeLLMClient(),
    )
    report = BuilderAgentV3(pipeline).build("Build Hello Project")
    assert report.final_result == "SUCCESS"


def test_compiler_and_pytest_runner_wrap_validator(tmp_path: Path) -> None:
    package = tmp_path / "hello_project"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "hello.py").write_text("def greet() -> str:\n    return 'hello'\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_hello.py").write_text("from hello_project.hello import greet\n\n\ndef test_greet():\n    assert greet() == 'hello'\n", encoding="utf-8")
    assert Compiler().run(tmp_path).success
    assert PytestRunner().run(tmp_path).success


def test_builder_reporter_writes_required_fields(tmp_path: Path) -> None:
    report = BuilderV3Report(
        "Hello Project",
        tmp_path,
        provider_used="fake-provider",
        compile_result=ValidationResult(True, "compile ok", passed=1),
        pytest_result=ValidationResult(True, "1 passed", passed=1),
    )
    path = BuilderReporter().write(report)
    content = path.read_text(encoding="utf-8")
    assert "Provider Used: fake-provider" in content
    assert "Final Result: SUCCESS" in content
