"""Progress tracking for sessions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Progress:
    """Progress percentage and ETA."""

    percent: float = 0.0
    eta: str = ""

    def update(self, completed: int, total: int, eta: str = "") -> None:
        """Update progress from completed and total counts."""
        self.percent = 100.0 if total <= 0 else round((completed / total) * 100, 2)
        self.eta = eta
