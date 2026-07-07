"""Session checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .models import utc_now


@dataclass
class Checkpoint:
    """Recoverable session checkpoint."""

    name: str
    data: dict[str, Any]
    checkpoint_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
