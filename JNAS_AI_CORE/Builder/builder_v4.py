"""Builder Agent V4 autonomous CLI pipeline."""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from urllib import request

from .utils import get_logger, strip_markdown_fences, write_text_file
from .validator import BuildValidator, ValidationResult


class V4LLMClient(Protocol):
    """LLM client contract for Builder V4."""

    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""


@dataclass(frozen=True)
class GeneratedFile:
    """One generated file parsed from an LLM response."""

    path: Path
    content: str


@dataclass
class BuilderV4Report:
    """Build report for Builder V4."""

    project_name: str
    project_root: Path
    provider: str
    milestone: int
    generated_files: list[Path] = field(default_factory=list)
    compile_result: ValidationResult | None = None
    test_result: ValidationResult | None = None
    retry_result: str = "not-run"
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def success(self) -> bool:
        """Return whether the build passed validation."""
        return bool(
            self.compile_result
            and self.compile_result.success
            and self.test_result
            and self.test_result.success
            and not self.errors
        )

    def to_markdown(self) -> str:
        """Render report markdown."""
        lines = [
            f"# BUILD REPORT: {self.project_name}",
            "",
            f"- Provider: `{self.provider}`",
            f"- Milestone: `{self.milestone}`",
            f"- Project root: `{self.project_root}`",
            f"- Final status: {'SUCCESS' if self.success else 'FAILED'}",
            f"- Execution time: {self.duration:.2f}s",
            "",
            "## Generated Files",
        ]
        lines.extend(f"- `{path}`" for path in self.generated_files) if self.generated_files else lines.append("- None")
        lines.extend(["", "## Compile Result", self._validation_text(self.compile_result)])
        lines.extend(["", "## Test Result", self._validation_text(self.test_result)])
        lines.extend(["", "## Retry Result", self.retry_result])
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in self.errors) if self.errors else lines.append("- None")
        return "\n".join(lines) + "\n"

    def _validation_text(self, result: ValidationResult | None) -> str:
        if result is None:
            return "NOT RUN"
        status = "PASS" if result.success else "FAIL"
        if not result.output:
            return status
        return f"{status}\n\n```text\n{result.output}\n```"


class DirectOllamaClient:
    """Direct local Ollama HTTP API client."""

    def __init__(
        self,
        host: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:7b",
        timeout: int = 300,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """Call Ollama /api/generate without interactive shell usage."""
        self._write_debug("logs/ollama_prompt.txt", prompt)
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": -1},
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = self._extract_content(body)
        self._write_debug("logs/ollama_response.txt", content)
        return content

    def _extract_content(self, body: dict[str, object]) -> str:
        message = body.get("message")
        if isinstance(message, dict) and "content" in message:
            return str(message["content"])
        return str(body.get("response", ""))

    def _write_debug(self, path: str, content: str) -> None:
        write_text_file(Path(path), content)


class FileResponseParser:
    """Parse filename-marked LLM responses into files."""

    _HEADER_PATTERN = re.compile(r"^\s*===FILE:(?P<path>[^=\r\n]+)===\s*$", re.MULTILINE)
    _END_PATTERN = re.compile(r"^\s*===END===\s*$", re.MULTILINE)

    def parse(self, response: str) -> list[GeneratedFile]:
        """Parse generated files from a marker-based response."""
        raw = response.strip()
        write_text_file(Path("logs") / "ollama_response.txt", response)
        end_match = self._END_PATTERN.search(raw)
        if end_match is None:
            raise ValueError("Parser error: missing terminal ===END=== marker.")
        content_region = raw[: end_match.start()].strip()
        trailing = raw[end_match.end() :].strip()
        if trailing:
            raise ValueError("Parser error: response contains text after ===END===.")
        headers = list(self._HEADER_PATTERN.finditer(content_region))
        if not headers:
            if "===FILE" in content_region:
                raise ValueError("Parser error: malformed FILE header. Expected ===FILE:path===.")
            raise ValueError("Parser error: response did not contain any ===FILE:path=== blocks.")
        files: list[GeneratedFile] = []
        for index, header in enumerate(headers):
            raw_path = header.group("path").strip()
            if not raw_path:
                raise ValueError("Parser error: FILE header path is empty.")
            next_start = headers[index + 1].start() if index + 1 < len(headers) else len(content_region)
            file_content = content_region[header.end() : next_start].strip("\r\n")
            files.append(GeneratedFile(Path(raw_path), strip_markdown_fences(file_content).rstrip() + "\n"))
        return files


class BuilderV4:
    """Autonomous project builder using direct Ollama API and file blocks."""

    def __init__(
        self,
        llm_client: V4LLMClient,
        parser: FileResponseParser | None = None,
        validator: BuildValidator | None = None,
        logger=None,
    ) -> None:
        self.llm_client = llm_client
        self.parser = parser or FileResponseParser()
        self.validator = validator or BuildValidator()
        self.logger = logger or get_logger(__name__)

    def build(
        self,
        project_name: str,
        output_directory: Path,
        provider: str = "ollama",
        milestone: int = 1,
    ) -> BuilderV4Report:
        """Build a project from CLI arguments."""
        started = time.perf_counter()
        project_root = output_directory / self._slugify(project_name)
        project_root.mkdir(parents=True, exist_ok=True)
        report = BuilderV4Report(project_name, project_root, provider, milestone)
        try:
            response = self.llm_client.generate(self._build_prompt(project_name, milestone))
            files = self._parse_with_retry(project_name, milestone, response, report)
            self._write_files(project_root, files, report)
            self._validate(project_root, report)
            if not report.success:
                self._repair_once(project_name, milestone, project_root, report)
        except Exception as exc:
            report.errors.append(str(exc))
            self.logger.exception("Builder V4 failed.")
        report.duration = time.perf_counter() - started
        write_text_file(project_root / "BUILD_REPORT.md", report.to_markdown())
        return report

    def _parse_with_retry(
        self,
        project_name: str,
        milestone: int,
        response: str,
        report: BuilderV4Report,
    ) -> list[GeneratedFile]:
        try:
            return self.parser.parse(response)
        except ValueError as exc:
            write_text_file(Path("logs") / "ollama_response.txt", response)
            self.logger.warning("Initial parse failed: %s", exc)
            retry_prompt = self._parser_repair_prompt(project_name, milestone, response, str(exc))
            retry_response = self.llm_client.generate(retry_prompt)
            report.retry_result = "parser-retry"
            return self.parser.parse(retry_response)

    def _build_prompt(self, project_name: str, milestone: int) -> str:
        return (
            "You are JNAS Builder Agent V4.\n"
            "Generate a complete Python project.\n"
            "Never ask for confirmation.\n"
            "IMPORTANT\n"
            "You MUST return ONLY file blocks.\n"
            "Do NOT write explanations.\n"
            "Do NOT use markdown code fences.\n"
            "Do NOT write any text before the first file.\n"
            "Do NOT write any text after the last file.\n"
            "\n"
            "Return every file EXACTLY like this, with one final ===END=== only:\n"
            "\n"
            "===FILE:README.md===\n"
            "<content>\n"
            "\n"
            "===FILE:requirements.txt===\n"
            "<content>\n"
            "\n"
            "===FILE:src/main.py===\n"
            "<python code>\n"
            "\n"
            "===FILE:src/job_search.py===\n"
            "<python code>\n"
            "\n"
            "===FILE:tests/test_job_search.py===\n"
            "<python code>\n"
            "\n"
            "===FILE:BUILD_REPORT.md===\n"
            "<markdown>\n"
            "\n"
            "===END===\n"
            "The only valid tokens outside file content are ===FILE:path=== and the final ===END===.\n"
            "Include tests when appropriate.\n"
            "Do not output TODO, placeholder code, fake imports, pass-only implementations, or explanations.\n"
            "Generated tests must match generated implementation.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n"
        )

    def _parser_repair_prompt(self, project_name: str, milestone: int, invalid_response: str, parser_error: str) -> str:
        return (
            "Your previous response was invalid and could not be parsed.\n"
            "Output ONLY valid file blocks.\n"
            "No markdown.\n"
            "No explanations.\n"
            "No prose.\n"
            "No code fences.\n"
            "Use this exact format with one final ===END=== only:\n\n"
            "===FILE:README.md===\n"
            "<content>\n\n"
            "===FILE:requirements.txt===\n"
            "<content>\n\n"
            "===FILE:src/main.py===\n"
            "<python code>\n\n"
            "===FILE:tests/test_main.py===\n"
            "<python test code>\n\n"
            "===END===\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n"
            f"Parser error: {parser_error}\n\n"
            "Previous invalid response:\n"
            f"{invalid_response}\n"
        )

    def _repair_prompt(self, project_name: str, milestone: int, report: BuilderV4Report) -> str:
        errors = "\n".join(
            part
            for part in (
                report.compile_result.output if report.compile_result else "",
                report.test_result.output if report.test_result else "",
            )
            if part
        )
        return (
            "Repair the generated project files.\n"
            "Return only files that must be replaced using ===FILE:path=== blocks and one final ===END===.\n"
            "No markdown. No explanations. No prose. No code fences.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n\n"
            "Validation errors:\n"
            f"{errors}\n"
        )

    def _write_files(self, project_root: Path, files: list[GeneratedFile], report: BuilderV4Report) -> None:
        for generated in files:
            target = self._safe_path(project_root, generated.path)
            write_text_file(target, generated.content)
            if target not in report.generated_files:
                report.generated_files.append(target)

    def _validate(self, project_root: Path, report: BuilderV4Report) -> None:
        report.compile_result = self.validator.compile_project(project_root)
        if report.compile_result.success:
            report.test_result = self.validator.test_project(project_root)

    def _repair_once(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        report: BuilderV4Report,
    ) -> None:
        repair_response = self.llm_client.generate(self._repair_prompt(project_name, milestone, report))
        files = self.parser.parse(repair_response)
        self._write_files(project_root, files, report)
        self._validate(project_root, report)
        report.retry_result = "success" if report.success else "failed"

    def _safe_path(self, project_root: Path, relative_path: Path) -> Path:
        root = project_root.resolve()
        target = (root / relative_path).resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"Generated path escapes project root: {relative_path}")
        return target

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
        return slug or "jnas_project"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Builder V4."""
    parser = argparse.ArgumentParser(prog="build_project", description="Build a project with JNAS Builder Agent V4.")
    parser.add_argument("--project", required=True, help="Project name to generate.")
    parser.add_argument("--output", required=True, type=Path, help="Directory where the project folder is created.")
    parser.add_argument("--provider", default="ollama", choices=["ollama"], help="LLM provider.")
    parser.add_argument("--milestone", default=1, type=int, help="Milestone number.")
    args = parser.parse_args(argv)

    client = DirectOllamaClient()
    report = BuilderV4(client).build(args.project, args.output, args.provider, args.milestone)
    print(report.to_markdown())
    return 0 if report.success else 1
