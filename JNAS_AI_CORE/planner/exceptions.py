"""Custom exceptions for the planning engine."""

from __future__ import annotations


class PlannerError(Exception):
    """Base exception for planner failures."""


class PlanValidationError(PlannerError):
    """Raised when an execution plan fails validation."""


class StrategyNotFound(PlannerError):
    """Raised when a requested planning strategy is unavailable."""
