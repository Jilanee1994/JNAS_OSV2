"""Exceptions for the JNAS machine learning framework."""

from __future__ import annotations


class MLFrameworkError(Exception):
    """Base exception for ML framework failures."""


class DatasetLoadError(MLFrameworkError):
    """Raised when a dataset cannot be loaded."""


class ModelNotFoundError(MLFrameworkError):
    """Raised when a model version cannot be found."""


class UnsupportedAlgorithmError(MLFrameworkError):
    """Raised when a requested algorithm is unavailable."""


class ModelPersistenceError(MLFrameworkError):
    """Raised when model persistence fails."""
