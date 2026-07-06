"""Recovery result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .analyzer import FailureAnalysis
from .history import RecoveryHistoryEntry
from .patcher import RecoveryPatch


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool
    message: str
    analysis: FailureAnalysis
    strategy: str
    retry_count: int = 0
    patch: RecoveryPatch | None = None
    validation_output: str = ""
    history_entry: RecoveryHistoryEntry | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
