"""Model training workflow."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import MLConfig
from .dataset import Dataset, DatasetLoader
from .evaluation import EvaluationMetrics, Evaluator
from .feature_engineering import FeatureEngineer
from .model_manager import ModelManager
from .persistence import ModelPersistence
from .preprocessing import Preprocessor


@dataclass(frozen=True)
class TrainingResult:
    """Result of an ML training run."""

    model_name: str
    algorithm: str
    model_path: Path
    metrics: EvaluationMetrics
    version: str


class ModelTrainer:
    """Train, evaluate, and persist ML models."""

    def __init__(
        self,
        config: MLConfig | None = None,
        model_manager: ModelManager | None = None,
        persistence: ModelPersistence | None = None,
        evaluator: Evaluator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config or MLConfig.from_config_manager()
        self.model_manager = model_manager or ModelManager()
        self.persistence = persistence or ModelPersistence(self.config.model_storage_dir)
        self.evaluator = evaluator or Evaluator()
        self.logger = logger or logging.getLogger("JNAS_AI_CORE.ml.trainer")
        self.dataset_loader = DatasetLoader()

    def train(
        self,
        dataset: Dataset | Path,
        target_column: str,
        model_name: str,
        algorithm: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> TrainingResult:
        """Train and persist a model."""
        dataset_obj = self.dataset_loader.load(dataset, target_column) if isinstance(dataset, Path) else dataset
        x_rows, y_values = dataset_obj.features_and_target(target_column)
        train_rows, test_rows, y_train, y_test = self._split(x_rows, y_values)
        preprocessor = Preprocessor()
        feature_engineer = FeatureEngineer()
        x_train_clean = preprocessor.fit_transform(train_rows)
        x_test_clean = preprocessor.transform(test_rows)
        x_train = feature_engineer.fit_transform(x_train_clean)
        x_test = feature_engineer.transform(x_test_clean)
        selected_algorithm = algorithm or self.config.default_algorithm
        model = self.model_manager.create_model(selected_algorithm, **(parameters or {}))
        model.fit(x_train, y_train)
        predictions = list(model.predict(x_test)) if x_test else list(model.predict(x_train))
        truth = y_test if x_test else y_train
        metrics = self.evaluator.evaluate(truth, predictions)
        metadata = {"model_name": model_name, "algorithm": selected_algorithm}
        model_path = self.persistence.save(
            model_name=model_name,
            model=model,
            metadata=metadata,
            metrics=metrics,
            artifacts={"preprocessor": preprocessor, "feature_engineer": feature_engineer},
        )
        self.logger.info("Trained model %s with algorithm %s.", model_name, selected_algorithm)
        return TrainingResult(model_name, selected_algorithm, model_path, metrics, model_path.name)

    def retrain(self, model_name: str, dataset: Dataset | Path, target_column: str, algorithm: str | None = None) -> TrainingResult:
        """Train a new version for an existing model."""
        return self.train(dataset, target_column, model_name, algorithm)

    def _split(
        self,
        x_rows: list[dict[str, Any]],
        y_values: list[Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[Any], list[Any]]:
        if len(x_rows) < 2:
            return x_rows, [], y_values, []
        test_count = max(1, int(len(x_rows) * self.config.test_size))
        split_at = max(1, len(x_rows) - test_count)
        return x_rows[:split_at], x_rows[split_at:], y_values[:split_at], y_values[split_at:]
