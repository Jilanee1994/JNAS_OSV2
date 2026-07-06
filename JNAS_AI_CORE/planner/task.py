"""Task model for execution plans."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    """A single planned task that may be executed by a future worker."""

    id: str
    title: str
    description: str
    priority: int = 1
    status: str = "pending"
    dependencies: list[str] = field(default_factory=list)
    estimated_duration: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
