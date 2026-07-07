"""Preprocessing helpers for tabular ML data."""

from __future__ import annotations

from collections import Counter
from typing import Any


class Preprocessor:
    """Handle missing values and prepare rows for feature engineering."""

    def fit_transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fit preprocessing statistics and transform rows."""
        self.fill_values = self._infer_fill_values(rows)
        return self.transform(rows)

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply missing-value handling to rows."""
        return [
            {key: self._clean_value(key, value) for key, value in row.items()}
            for row in rows
        ]

    def _infer_fill_values(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        values: dict[str, list[Any]] = {}
        for row in rows:
            for key, value in row.items():
                if value not in (None, ""):
                    values.setdefault(key, []).append(value)
        fills: dict[str, Any] = {}
        for key, column_values in values.items():
            numeric = [self._as_float(value) for value in column_values if self._as_float(value) is not None]
            if len(numeric) == len(column_values):
                fills[key] = sum(numeric) / len(numeric) if numeric else 0.0
            else:
                fills[key] = Counter(column_values).most_common(1)[0][0]
        return fills

    def _clean_value(self, key: str, value: Any) -> Any:
        if value in (None, ""):
            return self.fill_values.get(key, 0.0)
        numeric = self._as_float(value)
        return numeric if numeric is not None else value

    def _as_float(self, value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
