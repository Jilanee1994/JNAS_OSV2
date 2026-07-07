"""Daily report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class DailyReportGenerator:
    """Generate DAILY_REPORT.md for autonomous OS status."""

    def generate(
        self,
        path: Path = Path("DAILY_REPORT.md"),
        completed_tasks: list[Any] | None = None,
        pending_tasks: list[Any] | None = None,
        git_status: str = "",
        health: dict[str, Any] | None = None,
        model_usage: dict[str, Any] | None = None,
        provider_ranking: list[tuple[str, float]] | None = None,
        recommendations: list[str] | None = None,
    ) -> Path:
        """Write a daily Markdown report."""
        lines = [
            "# Daily AI OS Report",
            "",
            "## Completed Tasks",
            *[f"- {task}" for task in (completed_tasks or [])],
            "",
            "## Pending Tasks",
            *[f"- {task}" for task in (pending_tasks or [])],
            "",
            "## Git Status",
            git_status or "Unavailable",
            "",
            "## Health",
            str(health or {}),
            "",
            "## Model Usage",
            str(model_usage or {}),
            "",
            "## Provider Ranking",
            *[f"- {name}: {score:.3f}" for name, score in (provider_ranking or [])],
            "",
            "## Recommendations",
            *[f"- {item}" for item in (recommendations or ["No immediate action required."])],
            "",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
