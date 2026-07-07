"""Tests for the JNAS ML framework."""

from __future__ import annotations

import json
from pathlib import Path

from JNAS_AI_CORE.ml import (
    DatasetLoader,
    Evaluator,
    MLConfig,
    MLRegistry,
    ModelManager,
    ModelPersistence,
    ModelTrainer,
    Predictor,
)


class FakeToolRegistry:
    """Small registry double for ML tool registration tests."""

    def __init__(self) -> None:
        self.tools = []

    def register_tool(self, tool) -> None:
        self.tools.append(tool)


def sample_rows() -> list[dict[str, object]]:
    return [
        {"size": 1, "kind": "pdf", "label": "document"},
        {"size": 2, "kind": "pdf", "label": "document"},
        {"size": 8, "kind": "jpg", "label": "image"},
        {"size": 9, "kind": "jpg", "label": "image"},
        {"size": "", "kind": "png", "label": "image"},
    ]


def test_load_csv_and_json_datasets(tmp_path) -> None:
    csv_path = tmp_path / "files.csv"
    csv_path.write_text("size,kind,label\n1,pdf,document\n8,jpg,image\n", encoding="utf-8")
    json_path = tmp_path / "files.json"
    json_path.write_text(json.dumps(sample_rows()), encoding="utf-8")
    loader = DatasetLoader()

    csv_dataset = loader.load(csv_path, "label")
    json_dataset = loader.load(json_path, "label")

    assert len(csv_dataset.rows) == 2
    assert len(json_dataset.rows) == 5
    assert csv_dataset.features_and_target("label")[1] == ["document", "image"]


def test_train_save_load_predict_and_version_model(tmp_path) -> None:
    config = MLConfig(model_storage_dir=tmp_path / "models", default_algorithm="majority", test_size=0.4)
    trainer = ModelTrainer(config=config)
    dataset = DatasetLoader().from_rows(sample_rows(), "label")

    result = trainer.train(dataset, "label", "file_classifier", algorithm="majority")
    predictor = Predictor(config=config)
    predictions = predictor.predict("file_classifier", [{"size": 3, "kind": "pdf"}])

    assert result.model_path.exists()
    assert (result.model_path / "metadata.json").exists()
    assert (result.model_path / "model.pkl").exists()
    assert (result.model_path / "metrics.json").exists()
    assert predictions
    assert ModelPersistence(config.model_storage_dir).list_versions("file_classifier") == [result.version]


def test_evaluation_metrics() -> None:
    metrics = Evaluator().evaluate(["yes", "no", "yes"], ["yes", "yes", "yes"])

    assert metrics.accuracy == 2 / 3
    assert "yes" in metrics.confusion_matrix
    assert metrics.f1 >= 0


def test_supported_algorithms_include_required_names() -> None:
    algorithms = ModelManager().supported_algorithms()

    assert "random_forest" in algorithms
    assert "decision_tree" in algorithms
    assert "logistic_regression" in algorithms
    assert "naive_bayes" in algorithms
    assert "svm" in algorithms
    assert "knn" in algorithms
    assert "gradient_boosting" in algorithms
    assert "xgboost" in algorithms
    assert "lightgbm" in algorithms


def test_ml_model_registers_as_tool(tmp_path) -> None:
    config = MLConfig(model_storage_dir=tmp_path / "models", default_algorithm="majority")
    dataset = DatasetLoader().from_rows(sample_rows(), "label")
    result = ModelTrainer(config=config).train(dataset, "label", "file_classifier", algorithm="majority")
    registry = FakeToolRegistry()
    predictor = Predictor(config=config)

    tool = MLRegistry(registry).register_model("file_classifier", predictor, result.version)
    output = tool.execute({"rows": [{"size": 10, "kind": "png"}]})

    assert registry.tools == [tool]
    assert tool.metadata.category == "ml"
    assert output
