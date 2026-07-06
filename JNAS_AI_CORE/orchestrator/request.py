"""Request models for the JNAS AI Core orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class UserRequest:
    """Normalized user input accepted by the orchestrator."""

    user_input: str
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.user_input or not self.user_input.strip():
            raise ValueError("user_input must be a non-empty string.")
