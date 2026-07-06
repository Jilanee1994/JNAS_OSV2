"""Configuration validation."""

from __future__ import annotations

from typing import Any

from .exceptions import ConfigurationValidationError
from .schema import CONFIG_SCHEMA


class ConfigValidator:
    """Validate known configuration keys."""

    def validate(self, config: dict[str, Any]) -> bool:
        """Validate config values against the lightweight schema."""
        for dotted_key, expected_type in CONFIG_SCHEMA.items():
            value = self._get(config, dotted_key)
            if value is not None and not isinstance(value, expected_type):
                raise ConfigurationValidationError(f"Invalid type for {dotted_key}.")
        return True

    def _get(self, config: dict[str, Any], dotted_key: str) -> Any:
        current: Any = config
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current
