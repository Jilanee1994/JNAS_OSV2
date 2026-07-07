"""Configuration models for the ML framework."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.configuration import ConfigManager
except ImportError:
    ConfigManager = None


@dataclass(frozen=True)
class MLConfig:
    """Runtime configuration for ML model training and storage."""

    model_storage_dir: Path = Path("JNAS_AI_CORE/workspace/models")
    default_algorithm: str = "decision_tree"
    test_size: float = 0.2
    random_state: int = 42

    @classmethod
    def from_config_manager(cls, config_manager: Any | None = None) -> "MLConfig":
        """Create configuration from the existing Configuration Manager."""
        manager = config_manager or (ConfigManager() if ConfigManager is not None else None)
        if manager is None:
            return cls()
        return cls(
            model_storage_dir=Path(str(manager.get("ml.model_storage_dir", cls.model_storage_dir))),
            default_algorithm=str(manager.get("ml.default_algorithm", cls.default_algorithm)),
            test_size=float(manager.get("ml.test_size", cls.test_size)),
            random_state=int(manager.get("ml.random_state", cls.random_state)),
        )
