"""Retry policy for autonomous generation correction loops."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryManager:
    """Track retry allowance for compile-fix loops."""

    max_retries: int = 3

    def can_retry(self, attempt: int) -> bool:
        """Return whether another correction attempt is allowed."""
        return attempt < self.max_retries
