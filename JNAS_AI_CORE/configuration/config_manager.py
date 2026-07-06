"""Configuration manager with simple hierarchy merging."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_CONFIG
from .loader import ConfigLoader
from .validator import ConfigValidator


class ConfigManager:
    """Manage default, project, environment, and user configuration."""

    def __init__(
        self,
        loader: ConfigLoader | None = None,
        validator: ConfigValidator | None = None,
    ) -> None:
        self.loader = loader or ConfigLoader()
        self.validator = validator or ConfigValidator()
        self.config = deepcopy(DEFAULT_CONFIG)

    def load(
        self,
        project_config: Path | None = None,
        user_config: Path | None = None,
        env_prefix: str = "JNAS_",
    ) -> dict[str, Any]:
        """Load configuration hierarchy."""
        config = deepcopy(DEFAULT_CONFIG)
        self._merge(config, self.loader.load_file(project_config) if project_config else {})
        self._merge(config, self.loader.load_environment(env_prefix))
        self._merge(config, self.loader.load_file(user_config) if user_config else {})
        self.validator.validate(config)
        self.config = config
        return self.config

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Get a value by dotted key."""
        current: Any = self.config
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def _merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._merge(target[key], value)
            else:
                target[key] = value
