"""Configuration exceptions."""

from __future__ import annotations


class ConfigurationError(Exception):
    """Base configuration error."""


class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration is invalid."""
