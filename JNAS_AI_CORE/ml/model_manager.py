"""Model creation and lifecycle management."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .exceptions import UnsupportedAlgorithmError


class MajorityClassifier:
    """Small deterministic fallback classifier for lean local installs."""

    def fit(self, x_train: list[list[float]], y_train: list[Any]) -> "MajorityClassifier":
        """Fit by storing the most common label."""
        if not y_train:
            raise ValueError("Training labels cannot be empty.")
        self.label = Counter(y_train).most_common(1)[0][0]
        self.labels = sorted(set(y_train), key=str)
        return self

    def predict(self, x_data: list[list[float]]) -> list[Any]:
        """Predict the most common training label."""
        return [self.label for _ in x_data]

    def predict_proba(self, x_data: list[list[float]]) -> list[list[float]]:
        """Return deterministic class probabilities."""
        return [[1.0 if label == self.label else 0.0 for label in self.labels] for _ in x_data]


@dataclass(frozen=True)
class ModelSpec:
    """Description of a supported model algorithm."""

    algorithm: str
    estimator: Any
    optional_dependency: str | None = None


class ModelManager:
    """Create model estimators by algorithm name."""

    SUPPORTED_ALGORITHMS = [
        "random_forest",
        "decision_tree",
        "logistic_regression",
        "naive_bayes",
        "svm",
        "knn",
        "gradient_boosting",
        "xgboost",
        "lightgbm",
        "tensorflow",
        "pytorch",
        "majority",
    ]

    def create_model(self, algorithm: str, **parameters: Any) -> Any:
        """Create an estimator for the requested algorithm."""
        normalized = algorithm.lower().replace(" ", "_")
        if normalized == "majority":
            return MajorityClassifier()
        sklearn_model = self._create_sklearn_model(normalized, parameters)
        if sklearn_model is not None:
            return sklearn_model
        optional = self._create_optional_model(normalized, parameters)
        if optional is not None:
            return optional
        raise UnsupportedAlgorithmError(
            f"Algorithm '{algorithm}' requires an optional ML dependency that is not installed."
        )

    def supported_algorithms(self) -> list[str]:
        """Return algorithm names understood by the framework."""
        return list(self.SUPPORTED_ALGORITHMS)

    def _create_sklearn_model(self, algorithm: str, parameters: dict[str, Any]) -> Any | None:
        try:
            from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.naive_bayes import GaussianNB
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.svm import SVC
            from sklearn.tree import DecisionTreeClassifier
        except ImportError:
            return MajorityClassifier() if algorithm in self.SUPPORTED_ALGORITHMS else None

        factories = {
            "random_forest": RandomForestClassifier,
            "decision_tree": DecisionTreeClassifier,
            "logistic_regression": LogisticRegression,
            "naive_bayes": GaussianNB,
            "svm": SVC,
            "knn": KNeighborsClassifier,
            "gradient_boosting": GradientBoostingClassifier,
        }
        factory = factories.get(algorithm)
        if factory is None:
            return None
        if algorithm == "svm":
            parameters.setdefault("probability", True)
        return factory(**parameters)

    def _create_optional_model(self, algorithm: str, parameters: dict[str, Any]) -> Any | None:
        if algorithm == "xgboost":
            try:
                from xgboost import XGBClassifier
            except ImportError:
                return None
            return XGBClassifier(**parameters)
        if algorithm == "lightgbm":
            try:
                from lightgbm import LGBMClassifier
            except ImportError:
                return None
            return LGBMClassifier(**parameters)
        return None
