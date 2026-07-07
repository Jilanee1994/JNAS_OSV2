"""
builder.utils
-------------

Shared low-level utilities for the Builder Engine.

This module provides:
    - Logger factory
    - Markdown code-fence stripping
    - Filesystem helpers (used only as a fallback when ``FileTool``
      is unavailable)
    - A flexible-call helper (``call_flexible``) that lets the Builder
      Engine talk to already-implemented project components
      (``LLMManager``, ``FileTool``, ``ProjectReader``, ``ProjectScanner``,
      ``ContextBuilder``, ``CodeAgent``) without assuming one exact
      method signature. This keeps the Builder Engine decoupled from
      the concrete implementation details of those components while
      still satisfying the "reuse, do not duplicate" requirement.
    - ``run_pytest`` -- executes pytest as a subprocess and captures
      structured results.

No component in this module re-implements functionality that already
exists elsewhere in JNAS_AI_CORE (LLM calls, file I/O, project
scanning/reading, context building). It only adapts to those
components.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Protocol, runtime_checkable

__all__ = [
    "get_logger",
    "strip_markdown_fences",
    "ensure_dir",
    "write_text_file",
    "call_flexible",
    "PytestResult",
    "run_pytest",
    "LLMManagerProtocol",
    "FileToolProtocol",
    "ProjectReaderProtocol",
    "ProjectScannerProtocol",
    "ContextBuilderProtocol",
    "CodeAgentProtocol",
]


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create (or fetch) a configured ``logging.Logger``.

    Args:
        name: Logger name, typically ``__name__`` of the caller.
        level: Logging level. Defaults to ``logging.INFO``.

    Returns:
        A configured ``logging.Logger`` instance. Safe to call multiple
        times for the same name; handlers are not duplicated.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


# --------------------------------------------------------------------------- #
# Text / markdown handling
# --------------------------------------------------------------------------- #
_FENCE_PATTERN = re.compile(
    r"^```(?:[a-zA-Z0-9_+-]*)\n(.*?)(?:\n```)\s*$",
    re.DOTALL | re.MULTILINE,
)
_ANY_FENCE_LINE = re.compile(r"^\s*```[a-zA-Z0-9_+-]*\s*$", re.MULTILINE)


def strip_markdown_fences(text: str) -> str:
    """
    Remove Markdown code fences (and optional language hints) from LLM
    output, returning only the raw code content.

    Handles the common cases:
        - A single fenced block wrapping the entire response.
        - Fenced blocks embedded within surrounding prose (fences are
          stripped, inner content is kept).
        - Already-clean code with no fences (returned unchanged).

    Args:
        text: Raw text returned by the LLM.

    Returns:
        The text with Markdown code fences removed and surrounding
        whitespace trimmed.
    """
    if text is None:
        return ""

    candidate = text.strip()

    full_match = _FENCE_PATTERN.match(candidate)
    if full_match:
        return full_match.group(1).strip("\n")

    if "```" in candidate:
        # Strip individual fence delimiter lines, keep the content between.
        cleaned = _ANY_FENCE_LINE.sub("", candidate)
        return cleaned.strip()

    return candidate


# --------------------------------------------------------------------------- #
# Filesystem helpers (fallback only -- FileTool is preferred when available)
# --------------------------------------------------------------------------- #
def ensure_dir(path: Path) -> None:
    """
    Create a directory (and parents) if it does not already exist.

    Args:
        path: Directory path to create.

    Raises:
        OSError: If the directory cannot be created.
    """
    path.mkdir(parents=True, exist_ok=True)


def write_text_file(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write text content to a file, creating parent directories as needed.

    This is used strictly as a fallback path when ``FileTool`` is not
    injected into the Builder Engine (e.g. during isolated unit tests).

    Args:
        path: Destination file path.
        content: Text content to write.
        encoding: File encoding. Defaults to UTF-8.

    Raises:
        OSError: If the file cannot be written.
    """
    ensure_dir(path.parent)
    path.write_text(content, encoding=encoding)


# --------------------------------------------------------------------------- #
# Flexible adapter calling
# --------------------------------------------------------------------------- #
def call_flexible(
    obj: Any,
    method_names: Iterable[str],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Invoke the first available/compatible method found on ``obj``.

    Existing JNAS_AI_CORE components (``LLMManager``, ``FileTool``, etc.)
    may expose slightly different method names depending on their exact
    implementation. Rather than duplicating or reimplementing those
    components, the Builder Engine adapts to them by attempting a list
    of plausible method names, in order, and calling the first one that
    exists and accepts the given arguments.

    Args:
        obj: The target component instance (e.g. an ``LLMManager``).
        method_names: Candidate method names to try, in priority order.
        *args: Positional arguments forwarded to the resolved method.
        **kwargs: Keyword arguments forwarded to the resolved method.

    Returns:
        The return value of the first successfully invoked method.

    Raises:
        AttributeError: If none of ``method_names`` exist on ``obj``.
        TypeError: If matching methods exist but none accept the given
            arguments.
    """
    if obj is None:
        raise AttributeError("Cannot call methods on a None component.")

    last_error: Optional[Exception] = None
    found_any = False

    for name in method_names:
        method = getattr(obj, name, None)
        if method is None or not callable(method):
            continue
        found_any = True
        try:
            return method(*args, **kwargs)
        except TypeError as exc:
            # Signature mismatch -- try a no-kwargs fallback, then move on.
            last_error = exc
            try:
                return method(*args)
            except TypeError as exc2:
                last_error = exc2
                continue

    if not found_any:
        raise AttributeError(
            f"None of the expected methods {list(method_names)} were found "
            f"on object of type {type(obj).__name__}."
        )
    raise TypeError(
        f"Found candidate methods {list(method_names)} on "
        f"{type(obj).__name__}, but none accepted the provided arguments."
    ) from last_error


# --------------------------------------------------------------------------- #
# Pytest execution
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PytestResult:
    """Structured result of a pytest subprocess run."""

    success: bool
    return_code: int
    stdout: str
    stderr: str
    target: str


def run_pytest(target: Path, extra_args: Optional[list[str]] = None) -> PytestResult:
    """
    Run pytest against a target path (file or directory) as a subprocess.

    Args:
        target: File or directory to test.
        extra_args: Additional CLI arguments to pass to pytest.

    Returns:
        A ``PytestResult`` capturing success state, return code, and
        captured stdout/stderr.
    """
    args = [sys.executable, "-m", "pytest", str(target), "-v"]
    if extra_args:
        args.extend(extra_args)

    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        return PytestResult(
            success=completed.returncode == 0,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            target=str(target),
        )
    except subprocess.TimeoutExpired as exc:
        return PytestResult(
            success=False,
            return_code=-1,
            stdout=exc.stdout or "",
            stderr=f"pytest execution timed out: {exc}",
            target=str(target),
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to caller as failure
        return PytestResult(
            success=False,
            return_code=-1,
            stdout="",
            stderr=f"Failed to execute pytest: {exc}",
            target=str(target),
        )


# --------------------------------------------------------------------------- #
# Component protocols (documentation of the expected reuse contracts)
# --------------------------------------------------------------------------- #
@runtime_checkable
class LLMManagerProtocol(Protocol):
    """Expected interface subset of the existing ``LLMManager``."""

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        ...


@runtime_checkable
class FileToolProtocol(Protocol):
    """Expected interface subset of the existing ``FileTool``."""

    def write_file(self, path: str, content: str) -> Any:
        ...

    def read_file(self, path: str) -> str:
        ...


@runtime_checkable
class ProjectReaderProtocol(Protocol):
    """Expected interface subset of the existing ``ProjectReader``."""

    def read(self) -> Any:
        ...


@runtime_checkable
class ProjectScannerProtocol(Protocol):
    """Expected interface subset of the existing ``ProjectScanner``."""

    def scan(self) -> Any:
        ...


@runtime_checkable
class ContextBuilderProtocol(Protocol):
    """Expected interface subset of the existing ``ContextBuilder``."""

    def build(self, *args: Any, **kwargs: Any) -> str:
        ...


@runtime_checkable
class CodeAgentProtocol(Protocol):
    """Expected interface subset of the existing ``CodeAgent``."""

    def run(self, *args: Any, **kwargs: Any) -> Any:
        ...
