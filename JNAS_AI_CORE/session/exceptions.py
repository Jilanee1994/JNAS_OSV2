"""Session manager exceptions."""

from __future__ import annotations


class SessionError(Exception):
    """Base exception for session failures."""


class SessionNotFound(SessionError):
    """Raised when a session cannot be found."""


class SessionValidationError(SessionError):
    """Raised when session data is invalid."""


class SessionLockError(SessionError):
    """Raised when a session lock cannot be acquired."""


class SessionSchemaError(SessionValidationError):
    """Raised when persisted session JSON does not match the expected schema."""
