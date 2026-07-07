"""Prediction workflow for persisted ML models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import MLConfig
from .persistence import ModelPersistence


class Predictor:
    """Load models and run predictions."""

    def __init__(
        self,
        config: MLConfig | None = None,
        persistence: ModelPersistence | None = None,
    ) -> None:
        self.config = config or MLConfig.from_config_manager()
        self.persistence = persistence or ModelPersistence(self.config.model_storage_dir)

    def predict(self, model_name: str, rows: list[dict[str, Any]], version: str | None = None) -> list[Any]:
        """Predict labels for feature rows."""
        payload = self.persistence.load(model_name, version)
        model = payload["model"]
        artifacts = payload["artifacts"]
        preprocessor = artifacts["preprocessor"]
        feature_engineer = artifacts["feature_engineer"]
        clean_rows = preprocessor.transform(rows)
        vectors = feature_engineer.transform(clean_rows)
        return list(model.predict(vectors))

    def load_model(self, model_name: str, version: str | None = None) -> dict[str, Any]:
        """Load a persisted model payload."""
        return self.persistence.load(model_name, version)

    def model_path(self, model_name: str, version: str | None = None) -> Path:
        """Return the storage path for a model version."""
        versions = self.persistence.list_versions(model_name)
        selected = version or versions[-1]
        return self.config.model_storage_dir / model_name / selected
