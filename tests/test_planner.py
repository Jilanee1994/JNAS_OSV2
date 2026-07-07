"""Tests for the JNAS AI Core planning engine."""

from __future__ import annotations

import json

import pytest

from JNAS_AI_CORE.planner import (
    ExecutionPlan,
    Planner,
    PlanValidationError,
    Task,
)


def test_plan_creation_for_web_scraper() -> None:
    planner = Planner()

    plan = planner.create_plan("Build a web scraper")

    assert plan.goal == "Build a web scraper"
    assert plan.metadata["strategy"] == "development"
    assert [task.title for task in plan.tasks][:3] == [
        "Create project structure",
        "Create downloader",
        "Create parser",
    ]
    assert len(plan.tasks) == 10


def test_generic_planning_examples() -> None:
    planner = Planner()

    goals = [
        "Build a CRM",
        "Build a Telegram Bot",
        "Download books",
        "Analyze PDFs",
        "Create ML model",
        "Research a topic",
        "Organize files",
    ]

    plans = [planner.create_plan(goal) for goal in goals]

    assert all(plan.tasks for plan in plans)
    assert [plan.metadata["strategy"] for plan in plans] == [
        "development",
        "development",
        "automation",
        "analysis",
        "development",
        "research",
        "automation",
    ]


def test_validation() -> None:
    planner = Planner()
    plan = planner.create_plan("Analyze repository")

    assert planner.validate_plan(plan) is True


def test_optimization() -> None:
    planner = Planner()
    plan = ExecutionPlan(
        goal="Optimize order",
        tasks=[
            Task("task-2", "Second", "Second task", priority=2, dependencies=["task-1"]),
            Task("task-1", "First", "First task", priority=1),
        ],
    )

    optimized = planner.optimize_plan(plan)

    assert [task.id for task in optimized.tasks] == ["task-1", "task-2"]


def test_json_export() -> None:
    planner = Planner()
    plan = planner.create_plan("Build a web scraper")

    exported = planner.export_plan(plan, "json")
    data = json.loads(exported)

    assert data["goal"] == "Build a web scraper"
    assert data["tasks"][0]["title"] == "Create project structure"


def test_markdown_export() -> None:
    planner = Planner()
    plan = planner.create_plan("Build a web scraper")

    exported = planner.export_plan(plan, "markdown")

    assert "# Execution Plan: Build a web scraper" in exported
    assert "### Task 1: Create project structure" in exported


def test_dependency_validation() -> None:
    planner = Planner()
    plan = ExecutionPlan(
        goal="Invalid dependency",
        tasks=[
            Task("task-1", "First", "First task", dependencies=["missing"]),
        ],
    )

    with pytest.raises(PlanValidationError):
        planner.validate_plan(plan)


def test_duplicate_task_detection() -> None:
    planner = Planner()
    plan = ExecutionPlan(
        goal="Duplicate IDs",
        tasks=[
            Task("task-1", "First", "First task"),
            Task("task-1", "Duplicate", "Duplicate task"),
        ],
    )

    with pytest.raises(PlanValidationError):
        planner.validate_plan(plan)
