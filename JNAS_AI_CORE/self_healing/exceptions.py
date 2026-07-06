"""Custom exceptions for self-healing operations."""

from __future__ import annotations


class HealingError(Exception):
    """Base exception for self-healing failures."""


class PatchApplicationError(HealingError):
    """Raised when a generated patch cannot be applied."""


class RecoveryPolicyError(HealingError):
    """Raised when a recovery policy cannot select a valid action."""


class RecoveryFailed(HealingError):
    """Raised when recovery cannot complete successfully."""
