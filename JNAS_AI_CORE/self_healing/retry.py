"""Retry policy model for self-healing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """Configurable retry behavior."""

    max_retries: int = 2
    retry_delay: float = 0.0
    backoff: float = 1.0

    def can_retry(self, retry_count: int) -> bool:
        """Return whether another retry is allowed."""
        return retry_count < self.max_retries

    def delay_for(self, retry_count: int) -> float:
        """Return the delay for a retry attempt."""
        return self.retry_delay * (self.backoff ** max(retry_count, 0))
