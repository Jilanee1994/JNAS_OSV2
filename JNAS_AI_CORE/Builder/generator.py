"""
builder.generator
------------------

Wraps the existing ``LLMManager`` (and optionally ``ContextBuilder`` /
``CodeAgent``) to generate module source code, unit tests, and prompt
artifacts for the Builder Engine.

This module does NOT implement its own LLM calling logic -- it strictly
delegates to the already-implemented ``LLMManager`` via the flexible
adapter in ``builder.utils``. If ``LLMManager`` is unavailable or a
generation call fails, safe static fallbacks from ``builder.templates``
are used so the pipeline never hard-crashes.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from . import templates
from .utils import get_logger, strip_markdown_fences, call_flexible

__all__ = ["CodeGenerator"]


class CodeGenerator:
    """
    Generates module source code, unit tests, and prompt artifacts by
    delegating to the project's existing ``LLMManager``.

    This class has a single responsibility: turn a module name (plus
    optional project context) into generated text artifacts. It does
    not touch the filesystem -- that responsibility belongs to
    ``FileTool`` / ``BuilderEngine``.

    Attributes:
        llm_manager: The existing, already-implemented LLM manager
            instance used to perform all text generation.
        context_builder: Optional existing ``ContextBuilder`` used to
            enrich prompts with project context.
        logger: Module-scoped logger.
    """

    #: Candidate method names tried against the injected LLM manager,
    #: in priority order, to remain compatible with its real signature.
    _LLM_METHOD_CANDIDATES = ("generate", "generate_code", "complete", "chat", "run")

    #: Candidate method names tried against the injected context builder.
    _CONTEXT_METHOD_CANDIDATES = ("build", "build_context", "get_context", "run")

    def __init__(
        self,
        llm_manager: Any,
        context_builder: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize the CodeGenerator.

        Args:
            llm_manager: An instance of the existing ``LLMManager``.
                Must not be None -- code generation is not possible
                without it (fallback templates are used only for
                per-call failures, not for a missing manager entirely).
            context_builder: Optional existing ``ContextBuilder``
                instance used to gather project context for prompts.
            logger: Optional logger override.

        Raises:
            ValueError: If ``llm_manager`` is None.
        """
        if llm_manager is None:
            raise ValueError("CodeGenerator requires a non-None LLMManager instance.")

        self.llm_manager = llm_manager
        self.context_builder = context_builder
        self.logger = logger or get_logger(__name__)

    # ------------------------------------------------------------------ #
    # Context
    # ------------------------------------------------------------------ #
    def _gather_context(self, module_name: str) -> str:
        """
        Gather project context for a module using ``ContextBuilder``,
        if one was injected.

        Args:
            module_name: Name of the module being generated.

        Returns:
            A context string, or an empty string if no context builder
            is available or context gathering fails.
        """
        if self.context_builder is None:
            return ""
        try:
            result = call_flexible(
                self.context_builder,
                self._CONTEXT_METHOD_CANDIDATES,
                module_name,
            )
            return str(result) if result else ""
        except Exception as exc:  # noqa: BLE001 - context is best-effort, never fatal
            self.logger.warning(
                "ContextBuilder call failed for module '%s': %s", module_name, exc
            )
            return ""

    # ------------------------------------------------------------------ #
    # LLM invocation
    # ------------------------------------------------------------------ #
    def _invoke_llm(self, prompt: str) -> str:
        """
        Invoke the injected ``LLMManager`` with a prompt.

        Args:
            prompt: The full prompt to send.

        Returns:
            Raw text returned by the LLM.

        Raises:
            RuntimeError: If the LLM manager cannot be invoked with any
                known method signature.
        """
        try:
            result = call_flexible(self.llm_manager, self._LLM_METHOD_CANDIDATES, prompt)
        except (AttributeError, TypeError) as exc:
            raise RuntimeError(f"Failed to invoke LLMManager: {exc}") from exc

        if not isinstance(result, str):
            result = str(result)
        return result

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def generate_module_code(self, module_name: str) -> str:
        """
        Generate the source code for a new module.

        Args:
            module_name: Name of the module (e.g. ``"planner"``).

        Returns:
            Clean Python source code (Markdown fences stripped). Falls
            back to a minimal skeleton if generation fails.
        """
        context = self._gather_context(module_name)
        prompt = templates.module_generation_prompt(module_name, context)

        try:
            raw = self._invoke_llm(prompt)
            code = strip_markdown_fences(raw)
            if not code.strip():
                raise RuntimeError("LLM returned empty module code.")
            self.logger.info("Generated module code for '%s' (%d chars).", module_name, len(code))
            return code
        except Exception as exc:  # noqa: BLE001 - fall back safely
            self.logger.error(
                "Module generation failed for '%s': %s. Using fallback skeleton.",
                module_name,
                exc,
            )
            return templates.fallback_module_code(module_name)

    def generate_test_code(self, module_name: str, module_code: str) -> str:
        """
        Generate a pytest unit-test file for a generated module.

        Args:
            module_name: Name of the module under test.
            module_code: The generated source code of the module.

        Returns:
            Clean pytest source code (Markdown fences stripped). Falls
            back to a minimal smoke-test if generation fails.
        """
        prompt = templates.test_generation_prompt(module_name, module_code)

        try:
            raw = self._invoke_llm(prompt)
            code = strip_markdown_fences(raw)
            if not code.strip():
                raise RuntimeError("LLM returned empty test code.")
            self.logger.info("Generated test code for '%s' (%d chars).", module_name, len(code))
            return code
        except Exception as exc:  # noqa: BLE001 - fall back safely
            self.logger.error(
                "Test generation failed for '%s': %s. Using fallback tests.",
                module_name,
                exc,
            )
            return templates.fallback_test_code(module_name)

    def generate_prompt_artifact(self, module_name: str) -> str:
        """
        Build the ``prompt.txt`` artifact content for a module, using
        the same prompt that was (or would be) sent to the LLM.

        Args:
            module_name: Name of the module.

        Returns:
            Text content to persist as ``prompt.txt``.
        """
        context = self._gather_context(module_name)
        prompt = templates.module_generation_prompt(module_name, context)
        return templates.prompt_artifact(module_name, prompt)

    def generate_init_code(self, module_name: str) -> str:
        """
        Build the ``__init__.py`` content for a generated module package.

        Args:
            module_name: Name of the module package.

        Returns:
            Text content for ``__init__.py``.
        """
        return templates.init_file_content(module_name)
