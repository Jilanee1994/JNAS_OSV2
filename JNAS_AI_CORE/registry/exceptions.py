"""Custom exceptions for the Tool Registry."""

from __future__ import annotations


class ToolRegistryError(Exception):
    """Base exception for registry failures."""


class ToolRegistrationError(ToolRegistryError):
    """Raised when a tool cannot be registered."""


class ToolValidationError(ToolRegistryError):
    """Raised when a tool or metadata fails validation."""


class ToolNotFound(ToolRegistryError):
    """Raised when a requested tool does not exist."""


class ToolDiscoveryError(ToolRegistryError):
    """Raised when package discovery fails."""
