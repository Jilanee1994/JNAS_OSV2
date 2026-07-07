"""Feature engineering for tabular datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any


@dataclass
class FeatureEngineer:
    """Encode categorical values and scale numeric features."""

    categorical_values: dict[str, list[Any]] = field(default_factory=dict)
    numeric_columns: list[str] = field(default_factory=list)
    means: dict[str, float] = field(default_factory=dict)
    stds: dict[str, float] = field(default_factory=dict)
    feature_names: list[str] = field(default_factory=list)

    def fit_transform(self, rows: list[dict[str, Any]]) -> list[list[float]]:
        """Fit encoders and scalers, then transform rows."""
        self._fit(rows)
        return self.transform(rows)

    def transform(self, rows: list[dict[str, Any]]) -> list[list[float]]:
        """Transform rows into numeric feature vectors."""
        vectors = []
        for row in rows:
            vector: list[float] = []
            for column in self.numeric_columns:
                value = float(row.get(column, self.means.get(column, 0.0)))
                vector.append((value - self.means[column]) / self.stds[column])
            for column, values in self.categorical_values.items():
                current = row.get(column)
                vector.extend(1.0 if current == value else 0.0 for value in values)
            vectors.append(vector)
        return vectors

    def _fit(self, rows: list[dict[str, Any]]) -> None:
        columns = sorted({key for row in rows for key in row})
        self.numeric_columns = []
        self.categorical_values = {}
        for column in columns:
            values = [row.get(column) for row in rows if row.get(column) not in (None, "")]
            if values and all(isinstance(value, (int, float)) for value in values):
                self.numeric_columns.append(column)
                numeric = [float(value) for value in values]
                mean = sum(numeric) / len(numeric)
                variance = sum((value - mean) ** 2 for value in numeric) / max(len(numeric), 1)
                self.means[column] = mean
                self.stds[column] = sqrt(variance) or 1.0
            else:
                self.categorical_values[column] = sorted(set(values), key=str)
        self.feature_names = list(self.numeric_columns)
        for column, values in self.categorical_values.items():
            self.feature_names.extend(f"{column}={value}" for value in values)

    def select_features(self, vectors: list[list[float]], indexes: list[int]) -> list[list[float]]:
        """Select a subset of features by index."""
        return [[row[index] for index in indexes] for row in vectors]
