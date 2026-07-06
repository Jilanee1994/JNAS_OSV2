"""Session manager exceptions."""

from __future__ import annotations


class SessionError(Exception):
    """Base exception for session failures."""


class SessionNotFound(SessionError):
    """Raised when a session cannot be found."""


class SessionValidationError(SessionError):
    """Raised when session data is invalid."""
