"""Dashboard-ready metrics projection."""

from __future__ import annotations

from .metrics import MetricsSnapshot
from .reporter import MetricsReporter


class MetricsDashboard:
    """Provide lightweight dashboard data."""

    def __init__(self, reporter: MetricsReporter | None = None) -> None:
        self.reporter = reporter or MetricsReporter()

    def data(self, snapshot: MetricsSnapshot) -> dict:
        """Return dashboard-ready data."""
        return self.reporter.to_dict(snapshot)
