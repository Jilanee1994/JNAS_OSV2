"""Configuration-driven LLM providers for Builder Agent V3."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any
from urllib import error, request

try:
    from JNAS_AI_CORE.configuration import ConfigManager
    from JNAS_AI_CORE.llm_router import LLMRouter, ProviderResult
except ImportError:
    ConfigManager = None
    LLMRouter = None
    ProviderResult = None


@dataclass(frozen=True)
class ProviderConfig:
    """Normalized provider configuration for Builder V3."""

    name: str
    endpoint: str
    model: str
    provider_type: str
    capabilities: set[str] = field(default_factory=set)
    headers: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    api_key_env: str = ""


class ConfiguredLLMProvider:
    """HTTP LLM provider supporting configured provider payload styles."""

    def __init__(self, config: ProviderConfig, logger: logging.Logger | None = None) -> None:
        self.config = config
        self.name = config.name
        self.capabilities = config.capabilities or {"general", "code_generation", "builder"}
        self.enabled = config.enabled
        self.logger = logger or logging.getLogger(__name__)
        self._successes = 0
        self._failures = 0
        self._total_time = 0.0

    def generate(self, prompt: str, timeout: int = 120) -> Any:
        """Generate a response using the configured HTTP provider."""
        started = time.perf_counter()
        headers = self._headers()
        payload = json.dumps(self._payload(prompt)).encode("utf-8")
        req = request.Request(self.config.endpoint, data=payload, headers=headers)
        try:
            with request.urlopen(req, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            text = self._extract_response(body)
            duration = time.perf_counter() - started
            self._successes += 1
            self._total_time += duration
            return self._provider_result(text, True, duration)
        except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            duration = time.perf_counter() - started
            self._failures += 1
            self._total_time += duration
            return self._provider_result("", False, duration, str(exc))

    def health_score(self) -> float:
        """Return current provider health."""
        total = self._successes + self._failures
        if not self.enabled:
            return 0.0
        return self._successes / total if total else 1.0

    def average_response_time(self) -> float:
        """Return average provider response time."""
        total = self._successes + self._failures
        return self._total_time / total if total else 0.0

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", **self.config.headers}
        api_key = os.getenv(self.config.api_key_env) if self.config.api_key_env else ""
        if api_key and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _payload(self, prompt: str) -> dict[str, Any]:
        provider_type = self.config.provider_type.lower()
        if provider_type == "ollama":
            return {"model": self.config.model, "prompt": prompt, "stream": False}
        if provider_type == "gemini":
            return {"contents": [{"parts": [{"text": prompt}]}]}
        return {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

    def _extract_response(self, body: dict[str, Any]) -> str:
        provider_type = self.config.provider_type.lower()
        if provider_type == "ollama":
            return str(body.get("response", ""))
        if provider_type == "gemini":
            return str(body["candidates"][0]["content"]["parts"][0]["text"])
        return str(body["choices"][0]["message"]["content"])

    def _provider_result(self, text: str, success: bool, duration: float, error_text: str = "") -> Any:
        if ProviderResult is not None:
            return ProviderResult(self.name, text, success, duration, error_text)
        return {"provider": self.name, "response": text, "success": success, "duration": duration, "error": error_text}


class BuilderProviderFactory:
    """Create Builder V3 providers and routers from configuration."""

    def __init__(
        self,
        config_manager: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config_manager = config_manager or (ConfigManager() if ConfigManager is not None else None)
        self.logger = logger or logging.getLogger(__name__)

    def create_router(self) -> Any:
        """Create an LLMRouter configured with Builder V3 providers."""
        providers = self.create_providers()
        if LLMRouter is None:
            return _SimpleRouter(providers)
        return LLMRouter(providers=providers, config_manager=self.config_manager, logger=self.logger)

    def create_providers(self) -> list[ConfiguredLLMProvider]:
        """Create providers in configured priority order."""
        configs = [self._normalize_provider(item) for item in self._provider_configs()]
        configs = [config for config in configs if config.enabled]
        priority = self._priority()
        order = {name: index for index, name in enumerate(priority)}
        configs.sort(key=lambda config: order.get(config.name, len(order)))
        return [ConfiguredLLMProvider(config, logger=self.logger) for config in configs]

    def _provider_configs(self) -> list[dict[str, Any]]:
        if self.config_manager is None:
            return []
        providers = self.config_manager.get("builder_v3.providers", None)
        if providers is None:
            providers = self.config_manager.get("llm_router.providers", [])
        return list(providers)

    def _priority(self) -> list[str]:
        if self.config_manager is None:
            return ["ollama", "gemini", "groq", "openrouter"]
        return list(self.config_manager.get("builder_v3.provider_priority", ["ollama", "gemini", "groq", "openrouter"]))

    def _normalize_provider(self, data: dict[str, Any]) -> ProviderConfig:
        name = str(data["name"])
        provider_type = str(data.get("provider_type", name)).lower()
        return ProviderConfig(
            name=name,
            endpoint=str(data["endpoint"]),
            model=str(data.get("model", "")),
            provider_type=provider_type,
            capabilities=set(data.get("capabilities", ["general", "code_generation", "builder"])),
            headers=dict(data.get("headers", {})),
            enabled=bool(data.get("enabled", True)),
            api_key_env=str(data.get("api_key_env", "")),
        )


class _SimpleRouter:
    """Fallback router used only when the project LLMRouter is unavailable."""

    def __init__(self, providers: list[ConfiguredLLMProvider]) -> None:
        self.providers = providers

    def route(self, prompt: str, capability: str = "general", priority: int = 100, timeout: int = 120) -> Any:
        errors: list[str] = []
        for provider in self.providers:
            if capability not in provider.capabilities and "general" not in provider.capabilities:
                continue
            result = provider.generate(prompt, timeout=timeout)
            if getattr(result, "success", False):
                return result
            errors.append(str(getattr(result, "error", "")))
        if ProviderResult is not None:
            return ProviderResult("none", "", False, 0.0, "; ".join(errors) or "No providers available.")
        return {"provider": "none", "response": "", "success": False, "error": "; ".join(errors)}
