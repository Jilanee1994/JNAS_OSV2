"""Tests for metrics engine."""

from __future__ import annotations

import json

from JNAS_AI_CORE.metrics import MetricsCollector, MetricsReporter, MetricsStorage


def test_metrics_collection_and_report(tmp_path) -> None:
    collector = MetricsCollector()
    collector.record_task(True, 2.0)
    collector.record_task(False, 4.0)
    collector.record_recovery(True, retries=2)
    collector.record_usage("tool", "file_tool")

    report = MetricsReporter().to_json(collector.get_snapshot())
    data = json.loads(report)

    assert data["tasks_executed"] == 2
    assert data["successful_tasks"] == 1
    assert data["failed_tasks"] == 1
    assert data["average_execution_time"] == 3.0
    assert data["average_retries"] == 2.0
    assert data["tool_usage"]["file_tool"] == 1

    saved = MetricsStorage().save_report(tmp_path / "metrics.json", report)
    assert saved.exists()
