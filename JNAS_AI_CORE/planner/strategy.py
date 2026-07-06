"""Planning strategies for converting goals into tasks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .exceptions import StrategyNotFound
from .task import Task


class PlanningStrategy(ABC):
    """Base class for pluggable planning strategies."""

    name: str

    @abstractmethod
    def create_tasks(self, goal: str) -> list[Task]:
        """Create ordered tasks for a goal."""

    def _tasks_from_titles(self, titles: Iterable[str]) -> list[Task]:
        tasks = []
        previous_id = ""
        for index, title in enumerate(titles, start=1):
            task_id = f"task-{index}"
            dependencies = [previous_id] if previous_id else []
            tasks.append(
                Task(
                    id=task_id,
                    title=title,
                    description=f"{title} for the requested goal.",
                    priority=index,
                    dependencies=dependencies,
                    estimated_duration=1,
                )
            )
            previous_id = task_id
        return tasks


class SimpleStrategy(PlanningStrategy):
    """General-purpose strategy for small goals."""

    name = "simple"

    def create_tasks(self, goal: str) -> list[Task]:
        return self._tasks_from_titles(
            [
                "Understand goal",
                "Break goal into tasks",
                "Prepare execution order",
                "Review plan",
            ]
        )


class DevelopmentStrategy(PlanningStrategy):
    """Strategy for building products, systems, bots, models, and tools."""

    name = "development"

    def create_tasks(self, goal: str) -> list[Task]:
        return self._tasks_from_titles(self._select_titles(goal))

    def _select_titles(self, goal: str) -> list[str]:
        lowered = goal.lower()
        if "scraper" in lowered:
            return [
                "Create project structure",
                "Create downloader",
                "Create parser",
                "Create cleaner",
                "Create exporter",
                "Generate tests",
                "Run tests",
                "Fix errors",
                "Generate documentation",
                "Package project",
            ]
        if "crm" in lowered:
            return [
                "Define customer data model",
                "Design contact management workflow",
                "Create account and activity modules",
                "Add search and filtering",
                "Add import and export flow",
                "Generate tests",
                "Run tests",
                "Fix errors",
                "Generate user documentation",
                "Prepare deployment package",
            ]
        if "telegram" in lowered or "bot" in lowered:
            return [
                "Define bot commands",
                "Configure messaging interface",
                "Implement command handlers",
                "Add persistence layer",
                "Add error handling",
                "Generate tests",
                "Run tests",
                "Fix errors",
                "Generate usage documentation",
                "Prepare deployment package",
            ]
        if "ml" in lowered or "machine learning" in lowered or "model" in lowered:
            return [
                "Define prediction objective",
                "Prepare dataset",
                "Select model approach",
                "Train baseline model",
                "Evaluate model performance",
                "Tune model parameters",
                "Package model artifact",
                "Generate tests",
                "Document model behavior",
                "Prepare deployment package",
            ]
        return [
            "Analyze requirements",
            "Define system components",
            "Design data flow",
            "Implement core workflow",
            "Add integration points",
            "Generate tests",
            "Run tests",
            "Fix errors",
            "Generate documentation",
            "Package deliverable",
        ]


class AutomationStrategy(PlanningStrategy):
    """Strategy for automation workflows."""

    name = "automation"

    def create_tasks(self, goal: str) -> list[Task]:
        lowered = goal.lower()
        if "book" in lowered or "download" in lowered:
            return self._tasks_from_titles(
                [
                    "Identify source locations",
                    "Define download rules",
                    "Create download queue",
                    "Validate downloaded files",
                    "Organize output folders",
                    "Add retry handling",
                    "Generate activity report",
                ]
            )
        if "organize" in lowered or "files" in lowered:
            return self._tasks_from_titles(
                [
                    "Scan input folders",
                    "Classify file types",
                    "Define naming rules",
                    "Create target folders",
                    "Move files safely",
                    "Validate final structure",
                    "Generate organization report",
                ]
            )
        return self._tasks_from_titles(
            [
                "Identify trigger",
                "Map input sources",
                "Define automation steps",
                "Add error handling",
                "Generate tests",
                "Run dry run",
                "Document workflow",
            ]
        )


class AnalysisStrategy(PlanningStrategy):
    """Strategy for analysis and audit goals."""

    name = "analysis"

    def create_tasks(self, goal: str) -> list[Task]:
        if "pdf" in goal.lower():
            return self._tasks_from_titles(
                [
                    "Collect PDF files",
                    "Extract text and metadata",
                    "Identify document structure",
                    "Analyze key content",
                    "Validate extracted findings",
                    "Generate analysis report",
                ]
            )
        return self._tasks_from_titles(
            [
                "Collect inputs",
                "Inspect source material",
                "Identify patterns",
                "Validate findings",
                "Summarize recommendations",
                "Generate report",
            ]
        )


class ResearchStrategy(PlanningStrategy):
    """Strategy for research-oriented goals."""

    name = "research"

    def create_tasks(self, goal: str) -> list[Task]:
        return self._tasks_from_titles(
            [
                "Define research question",
                "Collect references",
                "Compare sources",
                "Extract findings",
                "Validate conclusions",
                "Prepare research summary",
            ]
        )


class StrategyEngine:
    """Registry-backed planning strategy selector."""

    def __init__(self, strategies: Iterable[PlanningStrategy] | None = None) -> None:
        self._strategies: dict[str, PlanningStrategy] = {}
        for strategy in strategies or self._default_strategies():
            self.register_strategy(strategy)

    def register_strategy(self, strategy: PlanningStrategy) -> None:
        """Register or replace a planning strategy."""
        self._strategies[strategy.name] = strategy

    def select_strategy(self, goal: str, strategy_name: str | None = None) -> PlanningStrategy:
        """Select a strategy by explicit name or goal heuristics."""
        if strategy_name:
            return self.get_strategy(strategy_name)

        lowered = goal.lower()
        if any(
            word in lowered
            for word in ("scraper", "app", "module", "code", "build", "crm", "bot", "model")
        ):
            return self.get_strategy("development")
        if any(
            word in lowered
            for word in (
                "automate",
                "automation",
                "schedule",
                "workflow",
                "download",
                "organize",
                "files",
                "books",
            )
        ):
            return self.get_strategy("automation")
        if any(word in lowered for word in ("analyze", "analysis", "audit", "review", "pdf")):
            return self.get_strategy("analysis")
        if any(word in lowered for word in ("research", "find", "compare", "study")):
            return self.get_strategy("research")
        return self.get_strategy("simple")

    def get_strategy(self, name: str) -> PlanningStrategy:
        """Return a registered strategy by name."""
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise StrategyNotFound(f"Planning strategy not found: {name}") from exc

    def list_strategies(self) -> list[str]:
        """Return registered strategy names."""
        return sorted(self._strategies)

    def _default_strategies(self) -> list[PlanningStrategy]:
        return [
            SimpleStrategy(),
            DevelopmentStrategy(),
            AutomationStrategy(),
            AnalysisStrategy(),
            ResearchStrategy(),
        ]
