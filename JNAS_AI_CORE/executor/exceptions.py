"""Custom exceptions for the execution engine."""

from __future__ import annotations


class ExecutionError(Exception):
    """Base exception for executor failures."""


class ExecutionValidationError(ExecutionError):
    """Raised when a plan or task cannot be executed safely."""


class ExecutionCancelled(ExecutionError):
    """Raised when execution is cancelled before completion."""
