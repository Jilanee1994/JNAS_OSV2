"""LLM provider interface for Builder Agent V2."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Protocol

try:
    from JNAS_AI_CORE.llm_router import LLMRouter
    from JNAS_AI_CORE.llm_router.provider import HTTPProvider, ProviderResult
except ImportError:
    LLMRouter = None
    HTTPProvider = None
    ProviderResult = None


class BaseLLMProvider(Protocol):
    """Minimal provider contract used by Builder Agent V2."""

    name: str
    capabilities: set[str]

    def generate(self, prompt: str, timeout: int = 120) -> object:
        """Generate text for a prompt."""

    def health_score(self) -> float:
        """Return a provider health score from 0.0 to 1.0."""


@dataclass
class BuilderLLMResponse:
    """Normalized LLM response returned to the Builder pipeline."""

    provider: str
    content: str
    success: bool
    error: str = ""


class _HTTPBuilderProvider:
    """Builder provider wrapper around the existing HTTP provider."""

    default_endpoint = ""
    default_model = ""
    response_field = "response"

    def __init__(
        self,
        endpoint: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        capabilities: set[str] | None = None,
    ) -> None:
        if HTTPProvider is None:
            raise RuntimeError("JNAS_AI_CORE.llm_router.provider.HTTPProvider is required.")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._provider = HTTPProvider(
            name=self.name,
            endpoint=endpoint or self.default_endpoint,
            model=model or self.default_model,
            capabilities=capabilities or {"general", "code_generation", "builder"},
            headers=headers,
            response_field=self.response_field,
        )
        self.capabilities = self._provider.capabilities

    def generate(self, prompt: str, timeout: int = 120) -> object:
        """Generate text through the underlying HTTP provider."""
        return self._provider.generate(prompt, timeout)

    def health_score(self) -> float:
        """Return the underlying provider health score."""
        return self._provider.health_score()


class OllamaProvider(_HTTPBuilderProvider):
    """Ollama HTTP provider for local generation."""

    name = "ollama"
    default_endpoint = "http://127.0.0.1:11434/api/generate"
    default_model = os.getenv("JNAS_OLLAMA_MODEL", "qwen2.5:7b")


class GeminiProvider(_HTTPBuilderProvider):
    """Gemini-compatible HTTP provider configured by environment or caller."""

    name = "gemini"
    default_endpoint = os.getenv("JNAS_GEMINI_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
    default_model = os.getenv("JNAS_GEMINI_MODEL", "gemini-pro")
    response_field = "text"


class GroqProvider(_HTTPBuilderProvider):
    """Groq-compatible HTTP provider configured by environment or caller."""

    name = "groq"
    default_endpoint = os.getenv("JNAS_GROQ_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions")
    default_model = os.getenv("JNAS_GROQ_MODEL", "llama-3.1-8b-instant")
    response_field = "text"


class OpenRouterProvider(_HTTPBuilderProvider):
    """OpenRouter-compatible HTTP provider configured by environment or caller."""

    name = "openrouter"
    default_endpoint = os.getenv("JNAS_OPENROUTER_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
    default_model = os.getenv("JNAS_OPENROUTER_MODEL", "openai/gpt-4o-mini")
    response_field = "text"


class BuilderLLMClient:
    """Provider-agnostic generation client for Builder Agent V2."""

    def __init__(
        self,
        router: object | None = None,
        capability: str = "code_generation",
        logger: logging.Logger | None = None,
    ) -> None:
        if router is None and LLMRouter is not None:
            router = LLMRouter()
        self.router = router
        self.capability = capability
        self.logger = logger or logging.getLogger(__name__)

    def generate(self, prompt: str, timeout: int = 120) -> BuilderLLMResponse:
        """Generate content through an injected router or compatible provider."""
        if self.router is None:
            raise RuntimeError("BuilderLLMClient requires an LLMRouter or compatible provider.")
        self.logger.info("LLM Request started.")
        if hasattr(self.router, "route"):
            result = self.router.route(prompt, capability=self.capability, timeout=timeout)
        else:
            result = self.router.generate(prompt, timeout)
        response = self._normalize(result)
        if not response.success:
            raise RuntimeError(response.error or "LLM generation failed.")
        self.logger.info("LLM Request completed by %s.", response.provider)
        return response

    def _normalize(self, result: object) -> BuilderLLMResponse:
        provider = str(getattr(result, "provider", getattr(result, "name", "unknown")))
        content = str(getattr(result, "response", getattr(result, "content", "")))
        success = bool(getattr(result, "success", True))
        error = str(getattr(result, "error", ""))
        if isinstance(result, str):
            return BuilderLLMResponse("injected", result, True)
        if isinstance(result, dict):
            return BuilderLLMResponse(
                str(result.get("provider", "dict")),
                str(result.get("response", result.get("content", ""))),
                bool(result.get("success", True)),
                str(result.get("error", "")),
            )
        return BuilderLLMResponse(provider, content, success, error)
