"""Metrics reporting."""

from __future__ import annotations

import json
from dataclasses import asdict

from .metrics import MetricsSnapshot


class MetricsReporter:
    """Generate JSON metrics reports."""

    def to_dict(self, snapshot: MetricsSnapshot) -> dict:
        """Convert snapshot to report dictionary."""
        data = asdict(snapshot)
        data["recovery_success_rate"] = snapshot.recovery_success_rate
        data["average_execution_time"] = snapshot.average_execution_time
        data["average_retries"] = snapshot.average_retries
        return data

    def to_json(self, snapshot: MetricsSnapshot) -> str:
        """Generate a JSON report."""
        return json.dumps(self.to_dict(snapshot), indent=4, sort_keys=True)
