"""Self-healing engine for JNAS AI Core."""

from __future__ import annotations

from .analyzer import FailureAnalysis, FailureAnalyzer
from .exceptions import HealingError, PatchApplicationError, RecoveryFailed, RecoveryPolicyError
from .history import RecoveryHistory, RecoveryHistoryEntry
from .patcher import CodePatcher, RecoveryPatch
from .policy import RecoveryPolicy
from .recovery import RecoveryResult
from .retry import RetryPolicy
from .self_healing import SelfHealingEngine

__all__ = [
    "CodePatcher",
    "FailureAnalysis",
    "FailureAnalyzer",
    "HealingError",
    "PatchApplicationError",
    "RecoveryFailed",
    "RecoveryHistory",
    "RecoveryHistoryEntry",
    "RecoveryPatch",
    "RecoveryPolicy",
    "RecoveryPolicyError",
    "RecoveryResult",
    "RetryPolicy",
    "SelfHealingEngine",
]
