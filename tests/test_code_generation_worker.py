"""Tests for the autonomous code generation worker."""

from __future__ import annotations

from pathlib import Path

from JNAS_AI_CORE.workers import CodeGenerationWorker, GeneratedFileWriter, RetryManager
from JNAS_AI_CORE.workers.build_validator import BuildValidationResult


class FakeLLMClient:
    """Deterministic fake client for worker tests."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


class FakeBuildValidator:
    """Deterministic compile validator for retry tests."""

    def __init__(self, results: list[BuildValidationResult]) -> None:
        self.results = results

    def validate(self, target: Path) -> BuildValidationResult:
        return self.results.pop(0)


def test_extracts_and_writes_marked_files(tmp_path) -> None:
    writer = GeneratedFileWriter()
    files = writer.extract_files(
        "===FILE:pkg/example.py===\nprint('ok')\n===END===\n"
    )
    written = writer.write_files(files, tmp_path)

    assert written == [tmp_path / "pkg" / "example.py"]
    assert written[0].read_text(encoding="utf-8") == "print('ok')\n"


def test_worker_generates_and_validates_project(tmp_path) -> None:
    worker = CodeGenerationWorker(
        llm_client=FakeLLMClient(["===FILE:app.py===\nprint('ok')\n===END==="]),
        build_validator=FakeBuildValidator([BuildValidationResult(True, "compiled", 0)]),
        retry_manager=RetryManager(max_retries=1),
    )

    result = worker.execute({"instruction": "create app", "target_root": str(tmp_path)})

    assert result.success is True
    assert result.retries == 0
    assert (tmp_path / "app.py").exists()
    assert worker.history.entries[0].final_status == "success"


def test_worker_retries_with_compiler_errors(tmp_path) -> None:
    worker = CodeGenerationWorker(
        llm_client=FakeLLMClient(
            [
                "===FILE:broken.py===\ndef bad(:\n===END===",
                "===FILE:broken.py===\ndef good():\n    return True\n===END===",
            ]
        ),
        build_validator=FakeBuildValidator(
            [
                BuildValidationResult(False, "SyntaxError: invalid syntax", 1),
                BuildValidationResult(True, "compiled", 0),
            ]
        ),
        retry_manager=RetryManager(max_retries=2),
    )

    result = worker.execute({"instruction": "create fixed app", "target_root": str(tmp_path)})

    assert result.success is True
    assert result.retries == 1
    assert "SyntaxError" in result.errors[0]
    assert "def good" in (tmp_path / "broken.py").read_text(encoding="utf-8")


def test_worker_stops_after_retry_limit(tmp_path) -> None:
    worker = CodeGenerationWorker(
        llm_client=FakeLLMClient(
            [
                "===FILE:broken.py===\ndef bad(:\n===END===",
                "===FILE:broken.py===\ndef still_bad(:\n===END===",
            ]
        ),
        build_validator=FakeBuildValidator(
            [
                BuildValidationResult(False, "SyntaxError 1", 1),
                BuildValidationResult(False, "SyntaxError 2", 1),
            ]
        ),
        retry_manager=RetryManager(max_retries=1),
    )

    result = worker.execute({"instruction": "create app", "target_root": str(tmp_path)})

    assert result.success is False
    assert result.retries == 1
    assert worker.history.entries[0].final_status == "failed"


def test_prompt_rules_prevent_manual_approval(tmp_path) -> None:
    worker = CodeGenerationWorker(
        llm_client=FakeLLMClient(["===FILE:x.py===\npass\n===END==="]),
        build_validator=FakeBuildValidator([BuildValidationResult(True, "compiled", 0)]),
    )

    result = worker.execute({"instruction": "create x", "target_root": str(tmp_path)})
    prompt = worker.history.entries[0].prompt

    assert result.success is True
    assert "Never ask for confirmation" in prompt
    assert "Never ask \"continue?\"" in prompt
    assert "Return only code" in prompt
