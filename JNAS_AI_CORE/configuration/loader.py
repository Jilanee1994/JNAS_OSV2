"""Configuration loading from JSON, simple YAML, and environment variables."""

from __future__ import annotations
from dotenv import load_dotenv

import json
import os
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Load configuration data from lightweight sources."""

    def load_file(self, path: Path) -> dict[str, Any]:
        """Load JSON or simple YAML from a path."""
        path = Path(path)
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return json.loads(text)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return self._load_simple_yaml(text)
        return {}

    def load_environment(self, prefix: str = "JNAS_") -> dict[str, Any]:
        """Load environment variables into nested config keys."""
        load_dotenv() 
        config: dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            path = key[len(prefix):].lower().split("__")
            self._set_nested(config, path, self._coerce(value))
        return config

    def _load_simple_yaml(self, text: str) -> dict[str, Any]:
        config: dict[str, Any] = {}
        section = None
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line.strip() or line.strip().startswith("#"):
                continue
            if not line.startswith(" ") and line.endswith(":"):
                section = line[:-1].strip()
                config.setdefault(section, {})
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = self._coerce(value.strip())
                if section and raw_line.startswith(" "):
                    config.setdefault(section, {})[key] = value
                else:
                    config[key] = value
        return config

    def _set_nested(self, config: dict[str, Any], path: list[str], value: Any) -> None:
        current = config
        for part in path[:-1]:
            current = current.setdefault(part, {})
        current[path[-1]] = value

    def _coerce(self, value: str) -> Any:
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
