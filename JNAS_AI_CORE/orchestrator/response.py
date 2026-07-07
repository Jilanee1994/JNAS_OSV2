"""Response models for orchestrator execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionResponse:
    """Structured result returned by the AI orchestrator."""

    success: bool
    message: str
    result: Any = None
    execution_time: float = 0.0
    errors: list[str] = field(default_factory=list)
