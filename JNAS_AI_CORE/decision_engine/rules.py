"""Rules engine for deterministic decisions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Rule:
    """A deterministic decision rule."""

    name: str
    predicate: Callable[[dict[str, Any]], bool]
    action: Callable[[dict[str, Any]], Any]
    priority: int = 100


class RulesEngine:
    """Evaluate ordered rules before ML or LLM routing."""

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = sorted(rules or [], key=lambda item: item.priority)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule."""
        self.rules.append(rule)
        self.rules.sort(key=lambda item: item.priority)

    def decide(self, task: dict[str, Any]) -> Any | None:
        """Return the first rule result or None."""
        for rule in self.rules:
            if rule.predicate(task):
                return rule.action(task)
        return None
