"""Evaluation metrics for classification models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvaluationMetrics:
    """Common classification metrics."""

    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: dict[str, dict[str, int]]
    roc_auc: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class Evaluator:
    """Compute lightweight classification metrics."""

    def evaluate(self, y_true: list[Any], y_pred: list[Any], probabilities: list[float] | None = None) -> EvaluationMetrics:
        """Evaluate predictions against ground truth labels."""
        labels = sorted(set(y_true) | set(y_pred), key=str)
        matrix = {str(actual): {str(predicted): 0 for predicted in labels} for actual in labels}
        for actual, predicted in zip(y_true, y_pred):
            matrix[str(actual)][str(predicted)] += 1
        total = len(y_true) or 1
        correct = sum(1 for actual, predicted in zip(y_true, y_pred) if actual == predicted)
        accuracy = correct / total
        precision_values = []
        recall_values = []
        for label in labels:
            true_positive = matrix[str(label)][str(label)]
            predicted_positive = sum(matrix[str(actual)][str(label)] for actual in labels)
            actual_positive = sum(matrix[str(label)][str(predicted)] for predicted in labels)
            precision_values.append(true_positive / predicted_positive if predicted_positive else 0.0)
            recall_values.append(true_positive / actual_positive if actual_positive else 0.0)
        precision = sum(precision_values) / len(labels) if labels else 0.0
        recall = sum(recall_values) / len(labels) if labels else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        roc_auc = self._roc_auc(y_true, probabilities) if probabilities else None
        return EvaluationMetrics(accuracy, precision, recall, f1, matrix, roc_auc)

    def _roc_auc(self, y_true: list[Any], probabilities: list[float]) -> float | None:
        labels = list(dict.fromkeys(y_true))
        if len(labels) != 2:
            return None
        positive = labels[-1]
        pairs = sorted(zip(probabilities, y_true), key=lambda item: item[0])
        positive_ranks = [rank for rank, (_, label) in enumerate(pairs, start=1) if label == positive]
        positives = len(positive_ranks)
        negatives = len(y_true) - positives
        if not positives or not negatives:
            return None
        return (sum(positive_ranks) - positives * (positives + 1) / 2) / (positives * negatives)
