"""
Unit tests for the Builder Engine (builder/ package).

All existing JNAS_AI_CORE components (LLMManager, FileTool,
ContextBuilder, etc.) are mocked here so these tests exercise only the
Builder Engine's own logic, independent of the real implementations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from JNAS_AI_CORE.Builder.builder import BuilderEngine
from JNAS_AI_CORE.Builder.generator import CodeGenerator
from JNAS_AI_CORE.Builder.reporter import BuildReport, BuildReporter
from JNAS_AI_CORE.Builder.tester import TestOutcome, TestRunner
from JNAS_AI_CORE.Builder.utils import (
    PytestResult,
    call_flexible,
    strip_markdown_fences,
)


# --------------------------------------------------------------------------- #
# utils
# --------------------------------------------------------------------------- #
class TestStripMarkdownFences:
    def test_strips_full_fenced_block(self) -> None:
        raw = "```python\nprint('hi')\n```"
        assert strip_markdown_fences(raw) == "print('hi')"

    def test_strips_fence_without_language(self) -> None:
        raw = "```\nx = 1\n```"
        assert strip_markdown_fences(raw) == "x = 1"

    def test_returns_clean_text_unchanged(self) -> None:
        raw = "x = 1\ny = 2"
        assert strip_markdown_fences(raw) == raw

    def test_handles_empty_string(self) -> None:
        assert strip_markdown_fences("") == ""

    def test_handles_none(self) -> None:
        assert strip_markdown_fences(None) == ""  # type: ignore[arg-type]


class TestCallFlexible:
    def test_calls_first_matching_method(self) -> None:
        class Component:
            def generate(self, prompt: str) -> str:
                return f"generated:{prompt}"

        result = call_flexible(Component(), ["missing", "generate"], "hello")
        assert result == "generated:hello"

    def test_raises_attribute_error_when_no_method_found(self) -> None:
        class Component:
            pass

        with pytest.raises(AttributeError):
            call_flexible(Component(), ["nonexistent"], "x")

    def test_raises_on_none_object(self) -> None:
        with pytest.raises(AttributeError):
            call_flexible(None, ["generate"], "x")


# --------------------------------------------------------------------------- #
# generator
# --------------------------------------------------------------------------- #
class TestCodeGenerator:
    def test_requires_llm_manager(self) -> None:
        with pytest.raises(ValueError):
            CodeGenerator(llm_manager=None)

    def test_generate_module_code_strips_fences(self) -> None:
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "```python\nclass Planner:\n    pass\n```"
        generator = CodeGenerator(llm_manager=mock_llm)

        code = generator.generate_module_code("planner")

        assert "```" not in code
        assert "class Planner" in code

    def test_generate_module_code_falls_back_on_llm_failure(self) -> None:
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM unreachable")
        generator = CodeGenerator(llm_manager=mock_llm)

        code = generator.generate_module_code("planner")

        assert "class Planner" in code
        assert "NotImplementedError" in code

    def test_generate_test_code_uses_module_code_context(self) -> None:
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "def test_x(): assert True"
        generator = CodeGenerator(llm_manager=mock_llm)

        code = generator.generate_test_code("planner", "class Planner: pass")

        assert "def test_x" in code

    def test_context_builder_failure_is_non_fatal(self) -> None:
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "class Planner:\n    pass"
        mock_context = MagicMock()
        mock_context.build.side_effect = RuntimeError("context error")

        generator = CodeGenerator(llm_manager=mock_llm, context_builder=mock_context)
        code = generator.generate_module_code("planner")

        assert "class Planner" in code


# --------------------------------------------------------------------------- #
# tester
# --------------------------------------------------------------------------- #
class TestTestRunner:
    def test_parses_passed_counts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_result = PytestResult(
            success=True,
            return_code=0,
            stdout="collected 2 items\n\n2 passed in 0.01s",
            stderr="",
            target="dummy",
        )
        monkeypatch.setattr(
            "JNAS_AI_CORE.Builder.tester.run_pytest",
            lambda target: fake_result,
        )

        runner = TestRunner()
        outcome = runner.run("planner", Path("dummy"))

        assert outcome.success is True
        assert outcome.passed_count == 2
        assert outcome.failed_count == 0

    def test_parses_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_result = PytestResult(
            success=False,
            return_code=1,
            stdout=(
                "collected 2 items\n\n"
                "FAILED planner/test_planner.py::test_run - AssertionError\n"
                "1 passed, 1 failed in 0.02s"
            ),
            stderr="",
            target="dummy",
        )
        monkeypatch.setattr(
            "JNAS_AI_CORE.Builder.tester.run_pytest",
            lambda target: fake_result,
        )

        runner = TestRunner()
        outcome = runner.run("planner", Path("dummy"))

        assert outcome.success is False
        assert outcome.passed_count == 1
        assert outcome.failed_count == 1
        assert any("test_run" in f for f in outcome.failure_summary)


# --------------------------------------------------------------------------- #
# reporter
# --------------------------------------------------------------------------- #
class TestBuildReporter:
    def test_report_success_property_true_when_no_errors_or_tests(self) -> None:
        report = BuildReport(module_name="planner", created_files=["a.py"])
        assert report.success is True

    def test_report_success_property_false_on_generation_error(self) -> None:
        report = BuildReport(
            module_name="planner",
            created_files=[],
            generation_errors=["boom"],
        )
        assert report.success is False

    def test_report_success_reflects_test_outcome(self) -> None:
        outcome = TestOutcome(
            module_name="planner",
            success=False,
            passed_count=1,
            failed_count=1,
            raw_result=PytestResult(False, 1, "", "", "dummy"),
        )
        report = BuildReport(module_name="planner", test_outcome=outcome)
        assert report.success is False

    def test_to_markdown_contains_module_name(self) -> None:
        report = BuildReport(module_name="planner")
        md = report.to_markdown()
        assert "planner" in md

    def test_save_report_writes_file(self, tmp_path: Path) -> None:
        reporter = BuildReporter(reports_dir=tmp_path)
        report = BuildReport(module_name="planner")

        saved_path = reporter.save_report(report)

        assert saved_path.exists()
        assert "planner" in saved_path.read_text()

    def test_print_summary_does_not_raise(self, capsys: pytest.CaptureFixture) -> None:
        reporter = BuildReporter()
        report = BuildReport(module_name="planner", created_files=["planner/planner.py"])

        reporter.print_summary(report)

        captured = capsys.readouterr()
        assert "planner" in captured.out


# --------------------------------------------------------------------------- #
# builder (orchestrator, fully mocked components)
# --------------------------------------------------------------------------- #
@pytest.fixture
def mock_llm_manager() -> Any:
    mock = MagicMock()
    mock.generate.side_effect = lambda prompt: (
        "class Planner:\n    def run(self):\n        return True"
        if "unit-test" not in prompt.lower()
        else "def test_run():\n    assert True"
    )
    return mock


@pytest.fixture
def mock_file_tool() -> Any:
    mock = MagicMock()
    written: dict[str, str] = {}

    def _write(path: str, content: str) -> None:
        written[path] = content

    mock.write_file.side_effect = _write
    mock._written = written
    return mock


class TestBuilderEngine:
    def test_build_creates_expected_files(
        self, tmp_path: Path, mock_llm_manager: Any, mock_file_tool: Any
    ) -> None:
        engine = BuilderEngine(
            project_root=tmp_path,
            llm_manager=mock_llm_manager,
            file_tool=mock_file_tool,
            project_reader=None,
            project_scanner=None,
            context_builder=None,
            code_agent=None,
        )

        report = engine.build("planner", run_tests=False)

        expected_suffixes = {
            "__init__.py",
            "planner.py",
            "prompt.txt",
            "test_planner.py",
        }
        created_names = {Path(f).name for f in report.created_files}
        assert expected_suffixes.issubset(created_names)
        assert not report.generation_errors

    def test_build_rejects_invalid_module_name(
        self, tmp_path: Path, mock_llm_manager: Any
    ) -> None:
        engine = BuilderEngine(
            project_root=tmp_path,
            llm_manager=mock_llm_manager,
            file_tool=MagicMock(),
        )
        with pytest.raises(ValueError):
            engine.build("not a valid name!")

    def test_build_requires_llm_manager(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError):
            BuilderEngine(project_root=tmp_path, llm_manager=None, file_tool=MagicMock())

    def test_build_runs_tests_when_requested(
        self, tmp_path: Path, mock_llm_manager: Any
    ) -> None:
        engine = BuilderEngine(
            project_root=tmp_path,
            llm_manager=mock_llm_manager,
            file_tool=None,  # force filesystem fallback so pytest can import real files
        )

        report = engine.build("sample", run_tests=True)

        assert report.test_outcome is not None
        assert (tmp_path / "sample" / "sample.py").exists()
        assert (tmp_path / "sample" / "test_sample.py").exists()
