"""Custom exceptions for JNAS AI Core memory operations."""

from __future__ import annotations


class MemoryError(Exception):
    """Base exception for memory manager failures."""


class MemoryNotFound(MemoryError):
    """Raised when a memory key does not exist."""


class MemorySerializationError(MemoryError):
    """Raised when a memory entry cannot be serialized or deserialized."""
