from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.Builder import builder_v4
from JNAS_AI_CORE.Builder.builder_v4 import BuilderV4, FileResponseParser


class FakeV4LLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


class AlwaysBadLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return conversational_response()


class FailingLLM:
    def generate(self, prompt: str) -> str:
        raise ConnectionError("ollama unavailable")


def valid_response() -> str:
    return """===FILE:hello.py===
def greet() -> str:
    return "hello"

===FILE:tests/test_hello.py===
from hello import greet


def test_greet() -> None:
    assert greet() == "hello"
===END===
"""


def weather_response() -> str:
    return """===FILE:README.md===
# WEATHER_DASHBOARD

Weather dashboard for city forecasts and temperatures.

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
from __future__ import annotations

import argparse


def get_forecast(city: str) -> dict[str, object]:
    return {"city": city, "temperature": 72, "condition": "Clear"}


def format_forecast(city: str) -> str:
    forecast = get_forecast(city)
    return f"Weather dashboard forecast for {forecast['city']}: {forecast['temperature']}F"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard CLI")
    parser.add_argument("--city", default="London")
    args = parser.parse_args(argv)
    print(format_forecast(args.city))
    return 0

===FILE:tests/test_main.py===
from src.main import format_forecast, get_forecast, main


def test_get_forecast_temperature() -> None:
    assert get_forecast("London")["temperature"] == 72


def test_format_forecast_mentions_weather_dashboard() -> None:
    assert "Weather dashboard" in format_forecast("London")


def test_weather_dashboard_cli(capsys) -> None:
    assert main(["--city", "London"]) == 0
    assert "forecast" in capsys.readouterr().out

===END===
"""


def broken_response() -> str:
    return """===FILE:hello.py===
def greet(:
    return "hello"

===FILE:tests/test_hello.py===
from hello import greet


def test_greet() -> None:
    assert greet() == "hello"
===END===
"""


def repaired_response() -> str:
    return """===FILE:hello.py===
def greet() -> str:
    return "hello"
===END===
"""


def conversational_response() -> str:
    return "Sure, here is the project:\n\n```python\nprint('hi')\n```"


def malformed_header_response() -> str:
    return """===FILE hello.py===
print("bad")
===END===
"""


def test_file_response_parser_extracts_files() -> None:
    files = FileResponseParser().parse(valid_response())
    assert [item.path.as_posix() for item in files] == ["hello.py", "tests/test_hello.py"]
    assert "def greet" in files[0].content


def test_file_response_parser_requires_end() -> None:
    try:
        FileResponseParser().parse("===FILE:hello.py===\nprint('x')\n")
    except ValueError as exc:
        assert "missing terminal ===END===" in str(exc)
    else:
        raise AssertionError("Expected missing END to fail.")


def test_file_response_parser_rejects_conversation() -> None:
    try:
        FileResponseParser().parse(conversational_response())
    except ValueError as exc:
        assert "missing terminal ===END===" in str(exc)
    else:
        raise AssertionError("Expected conversational response to fail.")


def test_file_response_parser_rejects_malformed_header() -> None:
    try:
        FileResponseParser().parse(malformed_header_response())
    except ValueError as exc:
        assert "malformed FILE header" in str(exc)
    else:
        raise AssertionError("Expected malformed header to fail.")


def test_builder_v4_builds_project_and_report(tmp_path: Path) -> None:
    report = BuilderV4(FakeV4LLM([valid_response()])).build("Hello", tmp_path, "ollama", 2)
    root = tmp_path / "hello"
    assert report.success
    assert (root / "hello.py").exists()
    assert (root / "tests" / "test_hello.py").exists()
    assert (root / "BUILD_REPORT.md").exists()
    assert report.compile_result is not None and report.compile_result.success
    assert report.test_result is not None and report.test_result.success


def test_builder_v4_runs_one_repair_cycle(tmp_path: Path) -> None:
    llm = FakeV4LLM([broken_response(), repaired_response()])
    report = BuilderV4(llm).build("Hello", tmp_path, "ollama", 1)
    assert report.success
    assert report.retry_result in {"preflight-repair-1", "success"}
    assert len(llm.prompts) >= 1


def test_builder_v4_retries_parser_failure(tmp_path: Path) -> None:
    llm = FakeV4LLM([conversational_response(), valid_response()])
    report = BuilderV4(llm).build("Hello", tmp_path, "ollama", 1)
    assert report.success
    assert report.retry_result == "parser-retry"
    assert "Previous invalid response" in llm.prompts[1]


def test_builder_v4_rejects_path_escape(tmp_path: Path) -> None:
    response = """===FILE:../escape.py===
x = 1
===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("Bad", tmp_path, "ollama", 1)
    assert not report.success
    assert any("escapes project root" in error for error in report.errors)


def test_builder_v4_sanitizes_project_root_paths(tmp_path: Path) -> None:
    response = """===FILE:applications/hello/README.md===
# Hello

===FILE:path/applications/hello/tests/test_job_search.py===
def test_placeholder() -> None:
    assert True

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("hello", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "hello"
    assert (root / "README.md").exists()
    assert (root / "tests").exists()
    assert not (root / "applications").exists()
    assert not (root / "path").exists()


def test_builder_v4_rejects_forbidden_path_directory_after_project_root(tmp_path: Path) -> None:
    response = """===FILE:applications/weather_dashboard/path/src/main.py===
print("bad")

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("WEATHER_DASHBOARD", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "weather_dashboard"
    assert not report.success
    assert any("forbidden directory token" in error for error in report.errors)
    assert not (root / "path").exists()


def test_builder_v4_normalizes_leading_path_wrapper_without_creating_folder(tmp_path: Path) -> None:
    response = """===FILE:path/applications/weather_dashboard/src/main.py===
from __future__ import annotations

import argparse


def get_forecast(city: str) -> dict[str, object]:
    return {"city": city, "temperature": 72}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard CLI")
    parser.add_argument("--city", default="London")
    parser.parse_args(argv)
    print("Weather dashboard forecast temperature")
    return 0

===FILE:path/applications/weather_dashboard/tests/test_main.py===
from src.main import get_forecast, main


def test_main() -> None:
    assert main([]) == 0


def test_forecast_temperature() -> None:
    assert get_forecast("London")["temperature"] == 72

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("WEATHER_DASHBOARD", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "weather_dashboard"
    assert report.success
    assert (root / "src" / "main.py").exists()
    assert not (root / "path").exists()


def test_builder_v4_rejects_absolute_generated_path(tmp_path: Path) -> None:
    response = """===FILE:/home/ubuntu/secret.py===
x = 1

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("hello", tmp_path / "applications", "ollama", 1)
    assert not report.success
    assert any("escapes project root" in error for error in report.errors)


def test_builder_v4_normalizes_absolute_project_path(tmp_path: Path) -> None:
    response = """===FILE:/applications/weather_dashboard/README.md===
# Weather Dashboard

City forecast and temperature dashboard.

===FILE:/applications/weather_dashboard/requirements.txt===

===FILE:/applications/weather_dashboard/src/__init__.py===

===FILE:/applications/weather_dashboard/src/main.py===
from __future__ import annotations

import argparse


def get_forecast(city: str) -> dict[str, object]:
    return {"city": city, "temperature": 72}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard")
    parser.add_argument("--city", default="London")
    args = parser.parse_args(argv)
    forecast = get_forecast(args.city)
    print(f"Weather dashboard forecast: {forecast['temperature']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

===FILE:/applications/weather_dashboard/tests/test_main.py===
from src.main import get_forecast, main


def test_main() -> None:
    assert main([]) == 0


def test_forecast_temperature() -> None:
    assert get_forecast("London")["temperature"] == 72

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("WEATHER_DASHBOARD", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "weather_dashboard"
    assert report.success
    assert (root / "src" / "main.py").exists()
    assert (root / "tests" / "test_main.py").exists()
    assert not (root / "applications").exists()


def test_builder_v4_rejects_normalized_path_escape(tmp_path: Path) -> None:
    response = """===FILE:applications/hello/../escape.py===
x = 1

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("hello", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "hello"
    assert not report.success
    assert any("escapes project root" in error for error in report.errors)
    assert not (tmp_path / "applications" / "escape.py").exists()
    assert not (root / "escape.py").exists()


def test_builder_v4_acceptance_hello_from_bad_llm(tmp_path: Path) -> None:
    report = BuilderV4(AlwaysBadLLM()).build("HELLO", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "hello"
    assert report.success
    assert (root / "src" / "main.py").exists()
    assert (root / "tests" / "test_main.py").exists()
    assert report.runtime_result is not None and report.runtime_result.success


def test_builder_v4_acceptance_hello_when_ollama_unavailable(tmp_path: Path) -> None:
    report = BuilderV4(FailingLLM()).build("HELLO", tmp_path / "applications", "ollama", 1)
    assert report.success
    assert report.retry_result in {"llm-fallback", "success"}


def test_builder_v4_acceptance_job_hunter_from_bad_llm(tmp_path: Path) -> None:
    report = BuilderV4(AlwaysBadLLM()).build("JOB_HUNTER", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "job_hunter"
    assert report.success
    assert (root / "src" / "job_search.py").exists()
    assert (root / "tests" / "test_job_search.py").exists()
    assert report.runtime_result is not None and report.runtime_result.success


def test_builder_v4_prompt_includes_build_agent_specification() -> None:
    prompt = BuilderV4(FakeV4LLM([]))._build_prompt("BUILD_AGENT", 1)

    assert "Project specification:" in prompt
    assert "orchestration agent" in prompt
    assert "create an execution plan" in prompt
    assert "src/job_search.py" not in prompt


def test_builder_v4_acceptance_build_agent_from_bad_llm(tmp_path: Path) -> None:
    report = BuilderV4(AlwaysBadLLM()).build("BUILD_AGENT", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "build_agent"

    assert report.success
    assert (root / "src" / "main.py").exists()
    assert "Build agent report" in (root / "src" / "main.py").read_text(encoding="utf-8")
    assert report.runtime_result is not None and report.runtime_result.success


def test_builder_v4_repeated_build_does_not_nest_or_duplicate(tmp_path: Path) -> None:
    builder = BuilderV4(AlwaysBadLLM())
    first = builder.build("HELLO", tmp_path / "applications", "ollama", 1)
    second = builder.build("HELLO", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "hello"
    assert first.success and second.success
    assert not (root / "applications").exists()
    assert not (root / "hello" / "hello").exists()
    assert len(list(root.rglob("main.py"))) == 1


def test_builder_v4_rejects_weather_dashboard_with_hello_semantics(tmp_path: Path) -> None:
    response = """===FILE:README.md===
# WEATHER_DASHBOARD

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
from __future__ import annotations

import argparse


def greet(name: str = "World") -> str:
    return f"Hello, {name}!"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hello application")
    parser.add_argument("--name", default="World")
    args = parser.parse_args(argv)
    print(greet(args.name))
    return 0

===FILE:tests/test_main.py===
from src.main import greet, main


def test_greet() -> None:
    assert greet("World") == "Hello, World!"

===END===
"""
    report = BuilderV4(FakeV4LLM([response]), retry_limit=0).build(
        "WEATHER_DASHBOARD",
        tmp_path / "applications",
        "ollama",
        1,
    )
    assert not report.success
    assert any("mismatched project terms" in error for error in report.errors)
    assert not (tmp_path / "applications" / "weather_dashboard").exists()


def test_builder_v4_repairs_weather_dashboard_semantics_with_project_specific_output(tmp_path: Path) -> None:
    response = """===FILE:README.md===
# WEATHER_DASHBOARD

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
from __future__ import annotations

import argparse


def greet(name: str = "World") -> str:
    return f"Hello, {name}!"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hello application")
    parser.add_argument("--name", default="World")
    args = parser.parse_args(argv)
    print(greet(args.name))
    return 0

===FILE:tests/test_main.py===
from src.main import greet, main


def test_greet() -> None:
    assert greet("World") == "Hello, World!"

===END===
"""
    llm = FakeV4LLM([response, weather_response()])
    report = BuilderV4(llm).build(
        "WEATHER_DASHBOARD",
        tmp_path / "applications",
        "ollama",
        1,
    )
    root = tmp_path / "applications" / "weather_dashboard"
    assert report.success
    assert len(llm.prompts) == 2
    source = (root / "src" / "main.py").read_text(encoding="utf-8").lower()
    tests = (root / "tests" / "test_main.py").read_text(encoding="utf-8").lower()
    assert "weather" in source
    assert "temperature" in source
    assert "--city" in source
    assert "greet" not in source
    assert "hello application" not in source
    assert "weather" in tests

def test_builder_v4_replaces_destination_transactionally_without_stale_tests(tmp_path: Path) -> None:
    root = tmp_path / "applications" / "weather_dashboard"
    (root / "src").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "src" / "main.py").write_text("def greet() -> str:\n    return 'hello'\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text(
        "from src.main import greet\n\n\ndef test_greet() -> None:\n    assert greet() == 'hello'\n",
        encoding="utf-8",
    )
    response = """===FILE:README.md===
# Weather Dashboard

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
from __future__ import annotations

import argparse


def current_temperature() -> int:
    return 72


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard")
    parser.parse_args(argv)
    print(f"Temperature: {current_temperature()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

===FILE:tests/test_main.py===
from src.main import current_temperature, main


def test_current_temperature() -> None:
    assert current_temperature() == 72


def test_main(capsys) -> None:
    assert main([]) == 0
    assert "Temperature" in capsys.readouterr().out

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("WEATHER_DASHBOARD", tmp_path / "applications", "ollama", 1)
    assert report.success
    assert report.generated_files
    assert "greet" not in (root / "tests" / "test_main.py").read_text(encoding="utf-8")
    assert "current_temperature" in (root / "src" / "main.py").read_text(encoding="utf-8")
    assert not (tmp_path / "applications" / ".builder_tmp" / "weather_dashboard").exists()


def test_builder_v4_does_not_replace_destination_when_candidate_is_inconsistent(tmp_path: Path) -> None:
    root = tmp_path / "applications" / "weather_dashboard"
    (root / "src").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "README.md").write_text("# Existing\n", encoding="utf-8")
    (root / "requirements.txt").write_text("\n", encoding="utf-8")
    (root / "src" / "__init__.py").write_text("\n", encoding="utf-8")
    (root / "src" / "main.py").write_text("def stable() -> str:\n    return 'stable'\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text(
        "from src.main import stable\n\n\ndef test_stable() -> None:\n    assert stable() == 'stable'\n",
        encoding="utf-8",
    )
    response = """===FILE:README.md===
# Broken Weather Dashboard

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
def weather() -> str:
    return "sunny"

===FILE:tests/test_main.py===
from src.main import greet


def test_greet() -> None:
    assert greet() == "hello"

===END===
"""
    report = BuilderV4(FakeV4LLM([response]), retry_limit=0).build(
        "WEATHER_DASHBOARD",
        tmp_path / "applications",
        "ollama",
        1,
    )
    assert not report.success
    assert "stable" in (root / "src" / "main.py").read_text(encoding="utf-8")
    assert "greet" not in (root / "src" / "main.py").read_text(encoding="utf-8")


def test_builder_v4_repairs_absolute_sibling_imports(tmp_path: Path) -> None:
    response = """===FILE:README.md===
# App

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/helper.py===
def value() -> str:
    return "ok"

===FILE:src/main.py===
from helper import value

def main(argv=None) -> int:
    print(value())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

===FILE:tests/test_main.py===
from src.main import main

def test_main(capsys):
    assert main([]) == 0
    assert "ok" in capsys.readouterr().out

===END===
"""
    report = BuilderV4(FakeV4LLM([response])).build("Import Repair", tmp_path, "ollama", 1)
    main_py = tmp_path / "import_repair" / "src" / "main.py"
    assert report.success
    assert "from .helper import value" in main_py.read_text(encoding="utf-8")


def test_builder_v4_repairs_nested_project_root_folder(tmp_path: Path) -> None:
    root = tmp_path / "applications" / "hello"
    nested = root / "applications"
    nested.mkdir(parents=True)
    (nested / "junk.py").write_text("x = 1\n", encoding="utf-8")
    report = BuilderV4(AlwaysBadLLM()).build("HELLO", tmp_path / "applications", "ollama", 1)
    assert report.success
    assert not nested.exists()


def test_builder_v4_repairs_undeclared_third_party_import(tmp_path: Path) -> None:
    response = """===FILE:README.md===
# Weather

===FILE:requirements.txt===

===FILE:src/__init__.py===

===FILE:src/main.py===
from flask import Flask

app = Flask(__name__)

def main(argv=None) -> int:
    print("Weather dashboard forecast temperature")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

===FILE:tests/test_main.py===
from src.main import main

def test_main() -> None:
    assert main([]) == 0

===END===
"""
    repair_response = """===FILE:src/main.py===
from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard")
    parser.add_argument("--city", default="London")
    parser.parse_args(argv)
    print("Weather dashboard forecast temperature")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

===END===
"""
    llm = FakeV4LLM([response, repair_response])
    report = BuilderV4(llm).build("WEATHER_DASHBOARD", tmp_path / "applications", "ollama", 1)
    root = tmp_path / "applications" / "weather_dashboard"
    assert report.success
    assert len(llm.prompts) >= 1
    assert not any("undeclared third-party dependency" in error for error in report.errors)


def test_builder_v4_declares_dependency_when_repair_still_requires_it(tmp_path: Path) -> None:
    root = tmp_path / "applications" / "weather_dashboard"
    root.mkdir(parents=True)
    builder = BuilderV4(FakeV4LLM([
        """===FILE:src/main.py===
from flask import Flask

app = Flask(__name__)

def main(argv=None) -> int:
    return 0

===END===
"""
    ]))
    builder._write_files(
        root,
        [
            builder_v4.GeneratedFile(Path("README.md"), "# Weather Dashboard\n\nCity forecast and temperature dashboard.\n"),
            builder_v4.GeneratedFile(Path("requirements.txt"), "\n"),
            builder_v4.GeneratedFile(Path("src/__init__.py"), "\n"),
            builder_v4.GeneratedFile(
                Path("src/main.py"),
                (
                    "from flask import Flask\n\n"
                    "app = Flask(__name__)\n\n"
                    "def get_temperature(city: str) -> int:\n"
                    "    return 72\n\n"
                    "def main(argv=None) -> int:\n"
                    "    print(f\"Weather dashboard temperature for {city}: {get_temperature('city')}\")\n"
                    "    return 0\n"
                ),
            ),
            builder_v4.GeneratedFile(
                Path("tests/test_main.py"),
                "from src.main import get_temperature\n\n\ndef test_weather_temperature() -> None:\n    assert get_temperature(\"London\") == 72\n",
            ),
        ],
        builder_v4.BuilderV4Report("WEATHER_DASHBOARD", root, "ollama", 1),
    )
    assert builder._preflight_validate(root) == []
    assert "flask" in (root / "requirements.txt").read_text(encoding="utf-8").lower()


def test_builder_v4_adds_generated_dependency_before_write(tmp_path: Path) -> None:
    root = tmp_path / "applications" / ".builder_tmp" / "weather_dashboard"
    builder = BuilderV4(FakeV4LLM([]), retry_limit=0)
    report = builder_v4.BuilderV4Report("WEATHER_DASHBOARD", root, "ollama", 1)
    builder._write_files(
        root,
        [
            builder_v4.GeneratedFile(Path("README.md"), "# Weather\n"),
            builder_v4.GeneratedFile(Path("requirements.txt"), "\n"),
            builder_v4.GeneratedFile(Path("src/__init__.py"), "\n"),
            builder_v4.GeneratedFile(
                Path("src/main.py"),
                "from flask import Flask\n\napp = Flask(__name__)\n\ndef main(argv=None) -> int:\n    return 0\n",
            ),
            builder_v4.GeneratedFile(Path("tests/test_main.py"), "from src.main import main\n"),
        ],
        report,
    )
    assert "flask" in (root / "requirements.txt").read_text(encoding="utf-8").lower()


def test_builder_v4_cli_returns_zero_on_success(tmp_path: Path, monkeypatch) -> None:
    class FakeClient:
        def generate(self, prompt: str) -> str:
            return valid_response()

    monkeypatch.setattr(builder_v4, "DirectOllamaClient", lambda: FakeClient())
    exit_code = builder_v4.main([
        "--project",
        "Hello",
        "--output",
        str(tmp_path),
        "--provider",
        "ollama",
        "--milestone",
        "3",
    ])
    assert exit_code == 0
    assert (tmp_path / "hello" / "BUILD_REPORT.md").exists()

