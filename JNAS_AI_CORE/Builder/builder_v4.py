"""Builder Agent V4 autonomous CLI pipeline."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
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


@dataclass(frozen=True)
class DependencyIssue:
    """Undeclared third-party dependency detected in a generated file."""

    path: Path
    package: str


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
    runtime_result: ValidationResult | None = None
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
            and self.runtime_result
            and self.runtime_result.success
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
        lines.extend(["", "## Runtime Result", self._validation_text(self.runtime_result)])
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

    _FORBIDDEN_PATH_PARTS = {"path", "filepath", "relative", "absolute"}
    _IMPORT_PACKAGE_MAP = {
        "PIL": "Pillow",
        "bs4": "beautifulsoup4",
        "cv2": "opencv-python",
        "flask": "Flask",
        "sklearn": "scikit-learn",
        "yaml": "PyYAML",
    }
    _TEST_ONLY_IMPORTS = {"pytest"}

    def __init__(
        self,
        llm_client: V4LLMClient,
        parser: FileResponseParser | None = None,
        validator: BuildValidator | None = None,
        logger=None,
        retry_limit: int = 3,
    ) -> None:
        self.llm_client = llm_client
        self.parser = parser or FileResponseParser()
        self.validator = validator or BuildValidator()
        self.logger = logger or get_logger(__name__)
        self.retry_limit = retry_limit

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
        tmp_root = output_directory / ".builder_tmp" / self._slugify(project_name)
        self._remove_directory(tmp_root)
        tmp_root.mkdir(parents=True, exist_ok=True)
        report = BuilderV4Report(project_name, project_root, provider, milestone)
        stage_report = BuilderV4Report(project_name, tmp_root, provider, milestone)
        try:
            try:
                response = self.llm_client.generate(self._build_prompt(project_name, milestone))
                files = self._parse_with_retry(project_name, milestone, response, stage_report)
            except Exception as exc:
                self.logger.warning("LLM generation failed; using deterministic recovery template: %s", exc)
                stage_report.retry_result = "llm-fallback"
                files = self._fallback_files(project_name)
            files = self._complete_required_files(project_name, files)
            files = self._repair_generated_dependencies(project_name, milestone, tmp_root, files)
            self._write_files(tmp_root, files, stage_report)
            self._validate_until_success(project_name, milestone, tmp_root, stage_report)
            self._copy_stage_report(stage_report, report, tmp_root, project_root)
            if stage_report.success:
                self._replace_project(tmp_root, project_root)
        except Exception as exc:
            report.errors.append(str(exc))
            self.logger.exception("Builder V4 failed.")
        report.duration = time.perf_counter() - started
        if report.success:
            write_text_file(project_root / "BUILD_REPORT.md", report.to_markdown())
        else:
            write_text_file(tmp_root / "BUILD_REPORT.md", report.to_markdown())
        return report

    def _copy_stage_report(
        self,
        stage_report: BuilderV4Report,
        report: BuilderV4Report,
        tmp_root: Path,
        project_root: Path,
    ) -> None:
        tmp_absolute = tmp_root.resolve()
        project_absolute = project_root.resolve()
        report.generated_files = [
            project_absolute / path.relative_to(tmp_absolute)
            for path in stage_report.generated_files
            if path.is_relative_to(tmp_absolute)
        ]
        report.compile_result = stage_report.compile_result
        report.test_result = stage_report.test_result
        report.runtime_result = stage_report.runtime_result
        report.retry_result = stage_report.retry_result
        report.errors = list(stage_report.errors)
        report.duration = stage_report.duration

    def _replace_project(self, tmp_root: Path, project_root: Path) -> None:
        project_root.parent.mkdir(parents=True, exist_ok=True)
        backup_root = project_root.with_name(f".{project_root.name}.builder_backup")
        self._remove_directory(backup_root)
        if project_root.exists():
            project_root.replace(backup_root)
        tmp_root.replace(project_root)
        self._remove_directory(backup_root)

    def _remove_directory(self, path: Path) -> None:
        if path.exists():
            shutil.rmtree(path)

    def _validate_until_success(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        report: BuilderV4Report,
    ) -> None:
        for attempt in range(self.retry_limit + 1):
            preflight_errors = self._preflight_validate(project_root)
            if preflight_errors:
                if attempt >= self.retry_limit:
                    report.errors.extend(preflight_errors)
                    return
                if self._has_semantic_errors(preflight_errors):
                    self._repair_semantic_project(project_name, milestone, project_root, preflight_errors, report)
                    report.retry_result = f"semantic-retry-{attempt + 1}"
                    continue
                self._repair_preflight(project_name, milestone, project_root, preflight_errors, report)
                report.retry_result = f"preflight-repair-{attempt + 1}"
                continue

            self._validate(project_root, report)
            if report.compile_result and not report.compile_result.success:
                if attempt >= self.retry_limit:
                    report.errors.append("Compile failed after retry limit.")
                    return
                self._repair_once(project_name, milestone, project_root, report, "compile")
                continue
            if report.test_result and not report.test_result.success:
                if attempt >= self.retry_limit:
                    report.errors.append("Pytest failed after retry limit.")
                    return
                self._repair_once(project_name, milestone, project_root, report, "pytest")
                continue

            report.runtime_result = self._runtime_validate(project_root)
            if report.runtime_result.success:
                report.retry_result = "success" if attempt else report.retry_result
                return
            if attempt >= self.retry_limit:
                report.errors.append("Runtime validation failed after retry limit.")
                return
            self._repair_once(project_name, milestone, project_root, report, "runtime")

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
            try:
                return self.parser.parse(retry_response)
            except ValueError:
                return self._fallback_files(project_name)

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
            "Required project structure:\n"
            "- README.md\n"
            "- requirements.txt\n"
            "- src/__init__.py\n"
            "- src/main.py\n"
            "- tests/test_*.py\n"
            "The application must start with: python -m src.main --help\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n"
        )

    def _semantic_repair_prompt(self, project_name: str, milestone: int, semantic_errors: list[str]) -> str:
        return (
            "Your previous project did not match the requested project specification.\n"
            "Regenerate the COMPLETE project from scratch.\n"
            "Return ONLY file blocks using ===FILE:path=== and one final ===END===.\n"
            "No markdown. No explanations. No prose. No code fences.\n"
            "Do not return Hello application code unless the requested project is HELLO.\n"
            "For WEATHER_DASHBOARD include weather, forecast, temperature, city, and dashboard concepts.\n"
            "For JOB_HUNTER include job, search, company, export, and candidate workflow concepts.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n\n"
            "Semantic validation errors:\n"
            f"{chr(10).join(semantic_errors)}\n"
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

    def _repair_prompt(self, project_name: str, milestone: int, report: BuilderV4Report, failure_type: str) -> str:
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
            f"Repair type: {failure_type}\n"
            "For compile failures, repair source files only.\n"
            "For pytest failures, repair only failing implementation or test files.\n"
            "For runtime failures, repair src/main.py or broken imports only.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n\n"
            "Validation errors:\n"
            f"{errors}\n"
        )

    def _dependency_repair_prompt(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        issues: list[DependencyIssue],
    ) -> str:
        issue_text = "\n".join(
            f"- {issue.path.as_posix()} imports undeclared dependency {issue.package}" for issue in issues
        )
        file_blocks = "\n\n".join(
            (
                f"===CURRENT_FILE:{path.as_posix()}===\n"
                f"{(project_root / path).read_text(encoding='utf-8')}"
            )
            for path in sorted({issue.path for issue in issues}, key=lambda item: item.as_posix())
        )
        return (
            "Repair ONLY the listed files to remove undeclared third-party imports when possible.\n"
            "Return ONLY replacement files using ===FILE:path=== blocks and one final ===END===.\n"
            "No markdown. No explanations. No prose. No code fences.\n"
            "Do not add new files. Do not regenerate the whole project.\n"
            "If the dependency is truly required, return the same corrected file content.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n\n"
            "Undeclared dependency issues:\n"
            f"{issue_text}\n\n"
            "Current files:\n"
            f"{file_blocks}\n"
        )

    def _generated_dependency_repair_prompt(
        self,
        project_name: str,
        milestone: int,
        files: list[GeneratedFile],
        issues: list[DependencyIssue],
    ) -> str:
        issue_text = "\n".join(
            f"- {issue.path.as_posix()} imports undeclared dependency {issue.package}" for issue in issues
        )
        by_path = {item.path: item for item in files}
        file_blocks = "\n\n".join(
            f"===CURRENT_FILE:{path.as_posix()}===\n{by_path[path].content}"
            for path in sorted({issue.path for issue in issues}, key=lambda item: item.as_posix())
            if path in by_path
        )
        return (
            "Repair ONLY the listed generated files before writing them to disk.\n"
            "Return ONLY replacement files using ===FILE:path=== blocks and one final ===END===.\n"
            "No markdown. No explanations. No prose. No code fences.\n"
            "Do not add new files. Do not regenerate the whole project.\n"
            "Prefer standard-library code over third-party dependencies when possible.\n"
            "If the dependency is truly required, return the same corrected file content.\n\n"
            f"Project name: {project_name}\n"
            f"Milestone: {milestone}\n\n"
            "Undeclared dependency issues:\n"
            f"{issue_text}\n\n"
            "Current generated files:\n"
            f"{file_blocks}\n"
        )

    def _repair_generated_dependencies(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        files: list[GeneratedFile],
    ) -> list[GeneratedFile]:
        normalized = self._normalize_generated_files(project_root, files)
        issues = self._generated_dependency_issues(normalized)
        if not issues:
            return normalized
        target_paths = {issue.path for issue in issues}
        by_path = {item.path: item for item in normalized}
        try:
            response = self.llm_client.generate(
                self._generated_dependency_repair_prompt(project_name, milestone, normalized, issues)
            )
            repairs = [
                GeneratedFile(self._normalize_generated_path(project_root, item.path), item.content)
                for item in self.parser.parse(response)
            ]
            for repair in repairs:
                if repair.path in target_paths:
                    by_path[repair.path] = repair
        except Exception as exc:
            self.logger.warning("Pre-write dependency repair failed; declaring dependencies: %s", exc)
        return self._declare_generated_dependencies(list(by_path.values()))

    def _normalize_generated_files(self, project_root: Path, files: list[GeneratedFile]) -> list[GeneratedFile]:
        by_path: dict[Path, GeneratedFile] = {}
        for item in files:
            normalized = self._normalize_generated_path(project_root, item.path)
            by_path.setdefault(normalized, GeneratedFile(normalized, item.content))
        return list(by_path.values())

    def _write_files(self, project_root: Path, files: list[GeneratedFile], report: BuilderV4Report) -> None:
        seen: set[Path] = set()
        normalized_files = self._normalize_generated_files(project_root, files)
        normalized_files = self._declare_generated_dependencies(normalized_files)
        for generated in normalized_files:
            normalized = generated.path
            if normalized in seen:
                raise ValueError(f"Duplicate generated file path: {normalized}")
            seen.add(normalized)
            target = self._safe_path(project_root, normalized)
            write_text_file(target, generated.content)
            if target not in report.generated_files:
                report.generated_files.append(target)

    def _normalize_generated_path(self, project_root: Path, generated_path: Path) -> Path:
        """Normalize LLM file paths so they are relative to the project root."""
        raw = generated_path.as_posix().strip()
        if not raw:
            raise ValueError("Generated file path is empty.")
        candidate = Path(raw)
        parts = [part for part in candidate.parts if part not in {"", "."}]
        if candidate.is_absolute():
            parts = self._absolute_project_parts(project_root, parts, generated_path)
        if any(part == ".." for part in parts):
            raise ValueError(f"Generated path escapes project root: {generated_path}")
        parts = self._strip_path_wrappers(project_root, parts)
        root_parts = list(project_root.parts)
        for index in range(len(parts)):
            suffix = parts[index:]
            if len(suffix) >= len(root_parts) and self._parts_equal(suffix[: len(root_parts)], root_parts):
                return self._validate_relative_path(Path(*suffix[len(root_parts) :]), generated_path)
        root_name = project_root.name
        for index, part in enumerate(parts):
            if part == root_name and index + 1 < len(parts):
                return self._validate_relative_path(Path(*parts[index + 1 :]), generated_path)
        if parts and parts[0] in {"path", "applications", "workspace"} and root_name in parts:
            root_index = parts.index(root_name)
            if root_index + 1 < len(parts):
                return self._validate_relative_path(Path(*parts[root_index + 1 :]), generated_path)
        normalized = Path(*parts)
        if normalized.parts and normalized.parts[0] == project_root.name:
            return self._validate_relative_path(Path(*normalized.parts[1:]), generated_path)
        return self._validate_relative_path(normalized, generated_path)

    def _strip_path_wrappers(self, project_root: Path, parts: list[str]) -> list[str]:
        lowered = [part.lower() for part in parts]
        root_name = project_root.name.lower()
        if root_name in lowered:
            root_index = lowered.index(root_name)
            return parts[root_index + 1 :]
        while parts and parts[0].lower() in self._FORBIDDEN_PATH_PARTS:
            parts = parts[1:]
        return parts

    def _absolute_project_parts(self, project_root: Path, parts: list[str], original_path: Path) -> list[str]:
        root_name = project_root.name.lower()
        clean_parts = [part for part in parts if part not in {project_root.anchor, "\\", "/"}]
        lowered = [part.lower() for part in clean_parts]
        if root_name not in lowered:
            raise ValueError(f"Generated path escapes project root: {original_path}")
        return clean_parts

    def _validate_relative_path(self, relative_path: Path, original_path: Path) -> Path:
        if not relative_path.parts:
            raise ValueError(f"Generated file path is invalid: {original_path}")
        if any(part.lower() in self._FORBIDDEN_PATH_PARTS for part in relative_path.parts[:-1]):
            raise ValueError(f"Generated path contains forbidden directory token: {original_path}")
        if relative_path.is_absolute() or any(part == ".." for part in relative_path.parts):
            raise ValueError(f"Generated path escapes project root: {original_path}")
        return relative_path

    def _parts_equal(self, left: list[str], right: list[str]) -> bool:
        return [part.lower() for part in left] == [part.lower() for part in right]

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
        failure_type: str = "validation",
    ) -> None:
        repair_response = self.llm_client.generate(self._repair_prompt(project_name, milestone, report, failure_type))
        try:
            files = self.parser.parse(repair_response)
        except ValueError:
            files = self._fallback_files(project_name)
        files = self._targeted_repair_files(project_name, files, failure_type, report)
        self._write_files(project_root, files, report)
        self._validate(project_root, report)
        report.retry_result = "success" if report.success else "failed"

    def _preflight_validate(self, project_root: Path) -> list[str]:
        errors: list[str] = []
        self._repair_package_imports(project_root)
        for required in ("README.md", "requirements.txt", "src/__init__.py", "src/main.py"):
            if not (project_root / required).exists():
                errors.append(f"Missing required file: {required}")
        if not (project_root / "tests").exists() or not list((project_root / "tests").glob("test_*.py")):
            errors.append("Missing tests directory or test files.")
        duplicate_names = self._duplicate_filenames(project_root)
        errors.extend(f"Duplicate filename detected: {name}" for name in duplicate_names)
        duplicate_folders = self._duplicate_folders(project_root)
        errors.extend(f"Duplicate folder detected: {name}" for name in duplicate_folders)
        errors.extend(self._python_quality_errors(project_root))
        errors.extend(self._import_quality_errors(project_root))
        errors.extend(self._dependency_quality_errors(project_root))
        errors.extend(self._symbol_consistency_errors(project_root))
        errors.extend(self._semantic_consistency_errors(project_root))
        return errors

    def _has_semantic_errors(self, errors: list[str]) -> bool:
        return any(
            "missing semantic terms" in error
            or "missing project intent terms" in error
            or "mismatched project terms" in error
            for error in errors
        )

    def _repair_semantic_project(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        errors: list[str],
        report: BuilderV4Report,
    ) -> None:
        self._clear_directory(project_root)
        response = self.llm_client.generate(self._semantic_repair_prompt(project_name, milestone, errors))
        files = self.parser.parse(response)
        files = self._complete_required_files(project_name, files)
        files = self._repair_generated_dependencies(project_name, milestone, project_root, files)
        self._write_files(project_root, files, report)

    def _clear_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        for child in path.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    def _repair_preflight(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        errors: list[str],
        report: BuilderV4Report,
    ) -> None:
        dependency_issues = self._dependency_issues(project_root)
        if dependency_issues and len(dependency_issues) == len(errors):
            self._repair_dependency_issues(project_name, milestone, project_root, dependency_issues, report)
            return
        self._remove_stale_root_python(project_root)
        self._remove_stale_tests(project_root)
        self._remove_nested_project_roots(project_root)
        files = self._fallback_files(project_name)
        self._write_files(project_root, files, report)

    def _repair_dependency_issues(
        self,
        project_name: str,
        milestone: int,
        project_root: Path,
        issues: list[DependencyIssue],
        report: BuilderV4Report,
    ) -> None:
        target_paths = {issue.path for issue in issues}
        try:
            response = self.llm_client.generate(
                self._dependency_repair_prompt(project_name, milestone, project_root, issues)
            )
            files = [
                item
                for item in self.parser.parse(response)
                if self._normalize_generated_path(project_root, item.path) in target_paths
            ]
            if files:
                self._write_files(project_root, files, report)
        except Exception as exc:
            self.logger.warning("Dependency repair generation failed; using targeted fallback files: %s", exc)
            self._write_files(project_root, self._fallback_files_for_paths(project_name, target_paths), report)
        remaining = [issue for issue in self._dependency_issues(project_root) if issue.path in target_paths]
        if remaining:
            self._add_requirements(project_root, {issue.package for issue in remaining})

    def _fallback_files_for_paths(self, project_name: str, target_paths: set[Path]) -> list[GeneratedFile]:
        by_path = {item.path: item for item in self._fallback_files(project_name)}
        return [by_path[path] for path in sorted(target_paths, key=lambda item: item.as_posix()) if path in by_path]

    def _remove_stale_root_python(self, project_root: Path) -> None:
        for path in project_root.glob("*.py"):
            path.unlink()

    def _remove_stale_tests(self, project_root: Path) -> None:
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            return
        for path in tests_dir.glob("test_*.py"):
            path.unlink()

    def _remove_nested_project_roots(self, project_root: Path) -> None:
        for folder_name in ("applications", "path", project_root.name):
            nested = project_root / folder_name
            if nested.exists() and nested.is_dir():
                for path in sorted(nested.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                nested.rmdir()

    def _runtime_validate(self, project_root: Path) -> ValidationResult:
        command = [sys.executable, "-m", "src.main", "--help"]
        started = time.perf_counter()
        completed = subprocess.run(command, cwd=project_root, capture_output=True, text=True, check=False, timeout=60)
        output = ((completed.stdout or "") + (completed.stderr or "")).strip()
        return ValidationResult(
            success=completed.returncode == 0,
            output=output,
            duration=time.perf_counter() - started,
            failed=0 if completed.returncode == 0 else 1,
            passed=1 if completed.returncode == 0 else 0,
            traceback="" if completed.returncode == 0 else output,
        )

    def _duplicate_filenames(self, project_root: Path) -> set[str]:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for path in project_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            if path.name in seen and path.name != "__init__.py":
                duplicates.add(path.name)
            seen.add(path.name)
        return duplicates

    def _duplicate_folders(self, project_root: Path) -> set[str]:
        forbidden = {"applications", "path", project_root.name}
        duplicates: set[str] = set()
        for path in project_root.rglob("*"):
            if path.is_dir() and path.name in forbidden and path != project_root:
                duplicates.add(path.name)
        return duplicates

    def _python_quality_errors(self, project_root: Path) -> list[str]:
        errors: list[str] = []
        bad_patterns = ("TODO", "FIXME", "your_module", "placeholder", "NotImplementedError")
        for path in project_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in bad_patterns:
                if pattern in text:
                    errors.append(f"{path.relative_to(project_root)} contains invalid placeholder marker: {pattern}")
            try:
                tree = ast.parse(text)
            except (SyntaxError, IndentationError) as exc:
                errors.append(f"{path.relative_to(project_root)} has syntax error: {exc}")
                continue
            function_names: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in function_names:
                        errors.append(f"{path.relative_to(project_root)} has duplicate function: {node.name}")
                    function_names.add(node.name)
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        errors.append(f"{path.relative_to(project_root)} has empty function: {node.name}")
        return errors

    def _repair_package_imports(self, project_root: Path) -> None:
        src_dir = project_root / "src"
        if not src_dir.exists():
            return
        module_names = {path.stem for path in src_dir.glob("*.py") if path.name != "__init__.py"}
        for path in src_dir.glob("*.py"):
            original = path.read_text(encoding="utf-8")
            updated = original
            for module_name in module_names:
                if path.stem == module_name:
                    continue
                updated = re.sub(
                    rf"(^\s*from\s+){re.escape(module_name)}(\s+import\s+)",
                    rf"\1.{module_name}\2",
                    updated,
                    flags=re.MULTILINE,
                )
            if updated != original:
                path.write_text(updated, encoding="utf-8")

    def _import_quality_errors(self, project_root: Path) -> list[str]:
        errors: list[str] = []
        src_dir = project_root / "src"
        if not src_dir.exists():
            return errors
        module_names = {path.stem for path in src_dir.glob("*.py") if path.name != "__init__.py"}
        for path in project_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, IndentationError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if path.parent == src_dir and node.level == 0 and module.split(".", 1)[0] in module_names:
                        errors.append(f"{path.relative_to(project_root)} uses absolute sibling import: {module}")
                    if node.level > 1:
                        errors.append(f"{path.relative_to(project_root)} uses invalid relative import level.")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_module = alias.name.split(".", 1)[0]
                        if path.parent == src_dir and root_module in module_names:
                            errors.append(f"{path.relative_to(project_root)} uses absolute sibling import: {alias.name}")
        return errors

    def _dependency_quality_errors(self, project_root: Path) -> list[str]:
        return [
            f"{issue.path} imports undeclared third-party dependency: {issue.package}"
            for issue in self._dependency_issues(project_root)
        ]

    def _symbol_consistency_errors(self, project_root: Path) -> list[str]:
        errors: list[str] = []
        for path in project_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, IndentationError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or node.level != 0 or not node.module:
                    continue
                module_path = self._local_import_module_path(project_root, node.module)
                if module_path is None:
                    continue
                if not module_path.exists():
                    errors.append(f"{path.relative_to(project_root)} imports missing module: {node.module}")
                    continue
                exported = self._exported_symbols(module_path)
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    if alias.name not in exported:
                        errors.append(
                            f"{path.relative_to(project_root)} imports missing symbol: {node.module}.{alias.name}"
                        )
        return errors

    def _local_import_module_path(self, project_root: Path, module_name: str) -> Path | None:
        parts = module_name.split(".")
        candidates: list[Path] = []
        if parts[0] == "src":
            candidates.append(project_root.joinpath(*parts).with_suffix(".py"))
            candidates.append(project_root.joinpath(*parts) / "__init__.py")
        elif (project_root / f"{parts[0]}.py").exists():
            candidates.append(project_root.joinpath(*parts).with_suffix(".py"))
        else:
            src_candidate = project_root / "src" / Path(*parts).with_suffix(".py")
            if src_candidate.exists():
                candidates.append(src_candidate)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0] if candidates else None

    def _exported_symbols(self, module_path: Path) -> set[str]:
        try:
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
        except (SyntaxError, IndentationError):
            return set()
        symbols: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    symbols.update(self._assigned_names(target))
            elif isinstance(node, ast.AnnAssign):
                symbols.update(self._assigned_names(node.target))
        return symbols

    def _assigned_names(self, node: ast.AST) -> set[str]:
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, (ast.Tuple, ast.List)):
            names: set[str] = set()
            for item in node.elts:
                names.update(self._assigned_names(item))
            return names
        return set()
    def _semantic_consistency_errors(self, project_root: Path) -> list[str]:
        project_key = project_root.name.lower()
        text = self._project_text(project_root)
        if not text.strip():
            return []
        if project_key == "weather_dashboard":
            return self._semantic_errors(
                project_root,
                text,
                required={"weather", "dashboard"},
                any_required={"forecast", "temperature", "city", "climate", "condition"},
                forbidden={"hello application", "hello, world", "hello world", "greet(", "def greet", "--name"},
            )
        if project_key == "job_hunter":
            return self._semantic_errors(
                project_root,
                text,
                required={"job"},
                any_required={"company", "csv", "export", "search", "hunter"},
                forbidden={"hello application", "hello, world", "hello world", "greet(", "def greet"},
            )
        if project_key in {"hello", "hello_world", "hello_project"}:
            return self._semantic_errors(
                project_root,
                text,
                required={"hello"},
                any_required={"greet", "world", "name"},
                forbidden=set(),
            )
        return []

    def _semantic_errors(
        self,
        project_root: Path,
        text: str,
        required: set[str],
        any_required: set[str],
        forbidden: set[str],
    ) -> list[str]:
        errors: list[str] = []
        missing = sorted(term for term in required if term not in text)
        if missing:
            errors.append(f"{project_root.name} missing semantic terms: {', '.join(missing)}")
        if any_required and not any(term in text for term in any_required):
            errors.append(f"{project_root.name} missing project intent terms: {', '.join(sorted(any_required))}")
        blocked = sorted(term for term in forbidden if term in text)
        if blocked:
            errors.append(f"{project_root.name} contains mismatched project terms: {', '.join(blocked)}")
        return errors

    def _project_text(self, project_root: Path) -> str:
        chunks: list[str] = []
        for pattern in ("README.md", "src/**/*.py", "tests/**/*.py"):
            for path in project_root.glob(pattern):
                if path.is_file() and "__pycache__" not in path.parts:
                    chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        return "\n".join(chunks).lower()


    def _dependency_issues(self, project_root: Path) -> list[DependencyIssue]:
        requirements = self._declared_requirements(project_root)
        local_modules = self._local_module_names(project_root)
        issues: list[DependencyIssue] = []
        for path in project_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            for module_name in self._imported_roots(path):
                if self._is_allowed_import(module_name, local_modules):
                    continue
                package_name = self._IMPORT_PACKAGE_MAP.get(module_name, module_name)
                if package_name.lower() not in requirements:
                    issues.append(DependencyIssue(path.relative_to(project_root), package_name))
        return issues

    def _add_requirements(self, project_root: Path, packages: set[str]) -> None:
        requirements_path = project_root / "requirements.txt"
        existing_text = requirements_path.read_text(encoding="utf-8") if requirements_path.exists() else ""
        existing = self._declared_requirements(project_root)
        additions = sorted(package for package in packages if package.lower() not in existing)
        if not additions:
            return
        lines = existing_text.splitlines()
        lines.extend(additions)
        requirements_path.write_text("\n".join(line for line in lines if line.strip()) + "\n", encoding="utf-8")

    def _declared_requirements(self, project_root: Path) -> set[str]:
        requirements_path = project_root / "requirements.txt"
        if not requirements_path.exists():
            return set()
        requirements: set[str] = set()
        for line in requirements_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            name = re.split(r"[<>=!~\[]", stripped, maxsplit=1)[0].strip()
            if name:
                requirements.add(name.lower())
        return requirements

    def _local_module_names(self, project_root: Path) -> set[str]:
        names = {"src"}
        names.update(path.stem for path in project_root.glob("*.py"))
        for folder in (project_root / "src", project_root / "tests"):
            if folder.exists():
                names.update(path.stem for path in folder.glob("*.py"))
        return names

    def _imported_roots(self, path: Path) -> set[str]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, IndentationError):
            return set()
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots.add(node.module.split(".", 1)[0])
        return roots

    def _is_allowed_import(self, module_name: str, local_modules: set[str]) -> bool:
        if module_name in local_modules or module_name in self._TEST_ONLY_IMPORTS:
            return True
        if module_name in sys.builtin_module_names:
            return True
        if module_name in getattr(sys, "stdlib_module_names", set()):
            return True
        spec = importlib.util.find_spec(module_name)
        if spec is None or spec.origin is None:
            return False
        origin = spec.origin.lower()
        return "site-packages" not in origin and "dist-packages" not in origin

    def _targeted_repair_files(
        self,
        project_name: str,
        files: list[GeneratedFile],
        failure_type: str,
        report: BuilderV4Report,
    ) -> list[GeneratedFile]:
        if failure_type == "compile":
            source_files = [item for item in files if item.path.as_posix().startswith("src/")]
            return source_files or self._fallback_source_files(project_name)
        if failure_type == "pytest":
            failed_names = {path.name for path in (report.test_result.failed_files if report.test_result else [])}
            if failed_names:
                matched = [item for item in files if item.path.name in failed_names]
                if matched:
                    return matched
            return files
        if failure_type == "runtime":
            matched = [item for item in files if item.path.as_posix() in {"src/main.py", "src/__init__.py"}]
            return matched or self._fallback_source_files(project_name)
        return files

    def _complete_required_files(self, project_name: str, files: list[GeneratedFile]) -> list[GeneratedFile]:
        by_path = {item.path.as_posix(): item for item in files}
        for item in self._fallback_files(project_name):
            by_path.setdefault(item.path.as_posix(), item)
        return list(by_path.values())

    def _fallback_source_files(self, project_name: str) -> list[GeneratedFile]:
        return [item for item in self._fallback_files(project_name) if item.path.as_posix().startswith("src/")]

    def _fallback_files(self, project_name: str) -> list[GeneratedFile]:
        key = self._slugify(project_name)
        if key == "job_hunter":
            return self._job_hunter_files()
        if key == "weather_dashboard":
            return self._weather_dashboard_files()
        return self._hello_files(project_name)

    def _hello_files(self, project_name: str) -> list[GeneratedFile]:
        return [
            GeneratedFile(Path("README.md"), f"# {project_name}\n\nGenerated by JNAS Builder.\n"),
            GeneratedFile(Path("requirements.txt"), "\n"),
            GeneratedFile(Path("src/__init__.py"), '"""Generated application package."""\n'),
            GeneratedFile(
                Path("src/main.py"),
                (
                    "from __future__ import annotations\n\n"
                    "import argparse\n\n\n"
                    "def greet(name: str = \"World\") -> str:\n"
                    "    return f\"Hello, {name}!\"\n\n\n"
                    "def main(argv: list[str] | None = None) -> int:\n"
                    "    parser = argparse.ArgumentParser(description=\"Hello application\")\n"
                    "    parser.add_argument(\"--name\", default=\"World\")\n"
                    "    args = parser.parse_args(argv)\n"
                    "    print(greet(args.name))\n"
                    "    return 0\n\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    raise SystemExit(main())\n"
                ),
            ),
            GeneratedFile(
                Path("tests/test_main.py"),
                (
                    "from src.main import greet, main\n\n\n"
                    "def test_greet() -> None:\n"
                    "    assert greet(\"JNAS\") == \"Hello, JNAS!\"\n\n\n"
                    "def test_main_runs(capsys) -> None:\n"
                    "    assert main([\"--name\", \"JNAS\"]) == 0\n"
                    "    assert \"Hello, JNAS!\" in capsys.readouterr().out\n"
                ),
            ),
        ]

    def _weather_dashboard_files(self) -> list[GeneratedFile]:
        return [
            GeneratedFile(Path("README.md"), "# WEATHER_DASHBOARD\n\nWeather dashboard CLI for city forecasts and temperatures.\n"),
            GeneratedFile(Path("requirements.txt"), "\n"),
            GeneratedFile(Path("src/__init__.py"), '"""WEATHER_DASHBOARD application."""\n'),
            GeneratedFile(
                Path("src/main.py"),
                (
                    "from __future__ import annotations\n\n"
                    "import argparse\n\n\n"
                    "FORECASTS = {\n"
                    "    \"london\": {\"temperature\": 18, \"condition\": \"Cloudy\"},\n"
                    "    \"mumbai\": {\"temperature\": 31, \"condition\": \"Humid\"},\n"
                    "    \"new york\": {\"temperature\": 24, \"condition\": \"Clear\"},\n"
                    "}\n\n\n"
                    "def get_forecast(city: str) -> dict[str, object]:\n"
                    "    key = city.strip().lower()\n"
                    "    return FORECASTS.get(key, {\"temperature\": 22, \"condition\": \"Mild\"})\n\n\n"
                    "def format_forecast(city: str) -> str:\n"
                    "    forecast = get_forecast(city)\n"
                    "    return f\"Weather dashboard for {city}: {forecast['temperature']}C and {forecast['condition']}\"\n\n\n"
                    "def main(argv: list[str] | None = None) -> int:\n"
                    "    parser = argparse.ArgumentParser(description=\"Weather dashboard CLI\")\n"
                    "    parser.add_argument(\"--city\", default=\"London\")\n"
                    "    args = parser.parse_args(argv)\n"
                    "    print(format_forecast(args.city))\n"
                    "    return 0\n\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    raise SystemExit(main())\n"
                ),
            ),
            GeneratedFile(
                Path("tests/test_main.py"),
                (
                    "from src.main import format_forecast, get_forecast, main\n\n\n"
                    "def test_get_forecast_contains_temperature() -> None:\n"
                    "    forecast = get_forecast(\"London\")\n"
                    "    assert forecast[\"temperature\"] == 18\n\n\n"
                    "def test_format_forecast_mentions_weather_dashboard() -> None:\n"
                    "    assert \"Weather dashboard\" in format_forecast(\"Mumbai\")\n\n\n"
                    "def test_weather_dashboard_cli_runs(capsys) -> None:\n"
                    "    assert main([\"--city\", \"London\"]) == 0\n"
                    "    assert \"Weather dashboard\" in capsys.readouterr().out\n"
                ),
            ),
        ]
    def _job_hunter_files(self) -> list[GeneratedFile]:
        return [
            GeneratedFile(Path("README.md"), "# JOB_HUNTER\n\nCLI job tracking and CSV export tool.\n"),
            GeneratedFile(Path("requirements.txt"), "\n"),
            GeneratedFile(Path("src/__init__.py"), '"""JOB_HUNTER application."""\n'),
            GeneratedFile(
                Path("src/job_search.py"),
                (
                    "from __future__ import annotations\n\n"
                    "import csv\n"
                    "import logging\n"
                    "from dataclasses import dataclass\n"
                    "from pathlib import Path\n\n"
                    "LOGGER = logging.getLogger(__name__)\n\n\n"
                    "@dataclass(frozen=True)\n"
                    "class Job:\n"
                    "    title: str\n"
                    "    company: str\n"
                    "    location: str\n"
                    "    url: str\n\n\n"
                    "def sample_jobs() -> list[Job]:\n"
                    "    return [\n"
                    "        Job(\"Python Developer\", \"JNAS\", \"Remote\", \"https://example.com/python\"),\n"
                    "        Job(\"Automation Engineer\", \"JNAS\", \"Remote\", \"https://example.com/automation\"),\n"
                    "    ]\n\n\n"
                    "def export_jobs(jobs: list[Job], output_path: Path) -> Path:\n"
                    "    output_path.parent.mkdir(parents=True, exist_ok=True)\n"
                    "    with output_path.open(\"w\", newline=\"\", encoding=\"utf-8\") as handle:\n"
                    "        writer = csv.DictWriter(handle, fieldnames=[\"title\", \"company\", \"location\", \"url\"])\n"
                    "        writer.writeheader()\n"
                    "        for job in jobs:\n"
                    "            writer.writerow(job.__dict__)\n"
                    "    LOGGER.info(\"Exported %s jobs to %s\", len(jobs), output_path)\n"
                    "    return output_path\n"
                ),
            ),
            GeneratedFile(
                Path("src/main.py"),
                (
                    "from __future__ import annotations\n\n"
                    "import argparse\n"
                    "import logging\n"
                    "from pathlib import Path\n\n"
                    "from .job_search import export_jobs, sample_jobs\n\n\n"
                    "def build_parser() -> argparse.ArgumentParser:\n"
                    "    parser = argparse.ArgumentParser(description=\"JOB_HUNTER CLI\")\n"
                    "    parser.add_argument(\"--output\", default=\"jobs.csv\")\n"
                    "    return parser\n\n\n"
                    "def main(argv: list[str] | None = None) -> int:\n"
                    "    logging.basicConfig(level=logging.INFO, format=\"%(levelname)s:%(message)s\")\n"
                    "    args = build_parser().parse_args(argv)\n"
                    "    path = export_jobs(sample_jobs(), Path(args.output))\n"
                    "    print(f\"Exported jobs to {path}\")\n"
                    "    return 0\n\n\n"
                    "if __name__ == \"__main__\":\n"
                    "    raise SystemExit(main())\n"
                ),
            ),
            GeneratedFile(
                Path("tests/test_job_search.py"),
                (
                    "import csv\n\n"
                    "from src.job_search import Job, export_jobs, sample_jobs\n"
                    "from src.main import main\n\n\n"
                    "def test_job_model() -> None:\n"
                    "    job = Job(\"Engineer\", \"JNAS\", \"Remote\", \"https://example.com\")\n"
                    "    assert job.title == \"Engineer\"\n\n\n"
                    "def test_csv_export(tmp_path) -> None:\n"
                    "    output = export_jobs(sample_jobs(), tmp_path / \"jobs.csv\")\n"
                    "    rows = list(csv.DictReader(output.open(encoding=\"utf-8\")))\n"
                    "    assert rows and rows[0][\"company\"] == \"JNAS\"\n\n\n"
                    "def test_cli_runs(tmp_path, capsys) -> None:\n"
                    "    output = tmp_path / \"jobs.csv\"\n"
                    "    assert main([\"--output\", str(output)]) == 0\n"
                    "    assert output.exists()\n"
                    "    assert \"Exported jobs\" in capsys.readouterr().out\n"
                ),
            ),
        ]

    def _safe_path(self, project_root: Path, relative_path: Path) -> Path:
        root = project_root.resolve()
        target = (root / relative_path).resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"Generated path escapes project root: {relative_path}")
        return target

    def _declare_generated_dependencies(self, files: list[GeneratedFile]) -> list[GeneratedFile]:
        issues = self._generated_dependency_issues(files)
        if not issues:
            return files
        required_packages = {issue.package for issue in issues}
        by_path = {item.path: item for item in files}
        requirements = by_path.get(Path("requirements.txt"), GeneratedFile(Path("requirements.txt"), "\n"))
        declared = self._declared_requirements_from_text(requirements.content)
        additions = sorted(package for package in required_packages if package.lower() not in declared)
        if not additions:
            return files
        lines = [line for line in requirements.content.splitlines() if line.strip()]
        lines.extend(additions)
        by_path[Path("requirements.txt")] = GeneratedFile(Path("requirements.txt"), "\n".join(lines) + "\n")
        return list(by_path.values())

    def _generated_dependency_issues(self, files: list[GeneratedFile]) -> list[DependencyIssue]:
        by_path = {item.path: item for item in files}
        requirements = self._declared_requirements_from_text(by_path.get(Path("requirements.txt"), GeneratedFile(Path("requirements.txt"), "")).content)
        local_modules = self._generated_local_module_names(files)
        issues: list[DependencyIssue] = []
        for item in files:
            if item.path.suffix != ".py" or "__pycache__" in item.path.parts:
                continue
            for module_name in self._imported_roots_from_text(item.content):
                if self._is_allowed_import(module_name, local_modules):
                    continue
                package_name = self._IMPORT_PACKAGE_MAP.get(module_name, module_name)
                if package_name.lower() not in requirements:
                    issues.append(DependencyIssue(item.path, package_name))
        return issues

    def _generated_local_module_names(self, files: list[GeneratedFile]) -> set[str]:
        names = {"src"}
        names.update(item.path.stem for item in files if item.path.parent == Path(".") and item.path.suffix == ".py")
        names.update(item.path.stem for item in files if item.path.parent.as_posix() in {"src", "tests"} and item.path.suffix == ".py")
        return names

    def _declared_requirements_from_text(self, content: str) -> set[str]:
        requirements: set[str] = set()
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            name = re.split(r"[<>=!~\[]", stripped, maxsplit=1)[0].strip()
            if name:
                requirements.add(name.lower())
        return requirements

    def _imported_roots_from_text(self, content: str) -> set[str]:
        try:
            tree = ast.parse(content)
        except (SyntaxError, IndentationError):
            return set()
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots.add(node.module.split(".", 1)[0])
        return roots

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


