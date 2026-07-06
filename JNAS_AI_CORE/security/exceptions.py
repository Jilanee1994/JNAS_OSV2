"""Security exceptions."""

from __future__ import annotations


class PermissionError(Exception):
    """Raised when an action is not permitted."""
