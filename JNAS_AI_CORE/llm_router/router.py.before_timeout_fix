
"""Configuration-driven LLM router."""

from __future__ import annotations


import os
import logging
from typing import Any

try:
    from JNAS_AI_CORE.configuration import ConfigManager
except ImportError:
    ConfigManager = None

from JNAS_AI_CORE.learning import LearningEngine, LearningRecord

from .provider import HTTPProvider, LLMProvider, ProviderResult


class LLMRouter:
    """Select the best available LLM provider with fallback."""

    def __init__(
        self,
        providers: list[LLMProvider] | None = None,
        learning_engine: LearningEngine | None = None,
        config_manager: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config_manager = config_manager or (ConfigManager() if ConfigManager is not None else None)
        self.providers = providers or self._providers_from_config()
        self.learning_engine = learning_engine or LearningEngine()
        self.logger = logger or logging.getLogger("JNAS_AI_CORE.llm_router")

    def route(self, prompt: str, capability: str = "general", priority: int = 100, timeout: int = 120) -> ProviderResult:
        """Route prompt to the best provider and fallback on failure."""
        failures: list[str] = []
        for provider in self.rank_providers(capability, priority):
            result = provider.generate(prompt, timeout)
            self.learning_engine.record(
                LearningRecord(prompt, result.provider, result.duration, result.success, [result.error] if result.error else [])
            )
            if result.success:
                self.logger.info("LLM request served by %s.", result.provider)
                return result
            failures.append(f"{result.provider}: {result.error}")
            self.logger.warning("Provider %s failed: %s", result.provider, result.error)
        return ProviderResult("none", "", False, 0.0, "; ".join(failures) or "No providers configured.")



    def _provider_headers(self, name: str) -> dict[str, str]:
        if name == "gemini":
            key = os.getenv("JNAS_GEMINI_API_KEY", "")
            return {"x-goog-api-key": key} if key else {}

        if name == "groq":
            key = os.getenv("JNAS_GROQ_API_KEY", "")
            return {"Authorization": f"Bearer {key}"} if key else {}

        if name == "openrouter":
            key = os.getenv("JNAS_OPENROUTER_API_KEY", "")
            return {"Authorization": f"Bearer {key}"} if key else {}

        return {}



    def rank_providers(self, capability: str = "general", priority: int = 100) -> list[LLMProvider]:
        """Rank providers by capability, health, success rate, and latency."""
        historical = dict(self.learning_engine.rank_providers())

        def score(provider: LLMProvider) -> float:
            capability_score = 1.0 if capability in provider.capabilities or "general" in provider.capabilities else 0.2
            health = provider.health_score()
            learned = historical.get(provider.name, 0.5)
            latency = getattr(provider, "average_response_time", lambda: 0.0)()
            latency_score = max(0.0, 1.0 - min(latency / max(priority, 1), 1.0))
            return capability_score * 0.35 + health * 0.30 + learned * 0.25 + latency_score * 0.10

        return sorted(self.providers, key=score, reverse=True)

    def _providers_from_config(self) -> list[LLMProvider]:
        if self.config_manager is None:
            return []
        configs = self.config_manager.get("llm_router.providers", [])
        providers = []
        for config in configs:
            name = config["name"]

            if name in {"gemini", "groq", "openrouter"}:
                headers = self._provider_headers(name)
                if not headers:
                    continue

            if not config.get("enabled", True) and name == "ollama":
                continue

            providers.append(
                HTTPProvider(
                    name=config["name"],
                    endpoint=config["endpoint"],
                    model=config.get("model", ""),
                    capabilities=set(config.get("capabilities", ["general"])),
                    headers={
			**dict(config.get("headers", {})),
			**self._provider_headers(config["name"]),
		}, 
                   response_field=config.get("response_field", "response"),
                )
            )
        return providers
