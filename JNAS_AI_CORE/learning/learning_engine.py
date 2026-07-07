"""Learning engine for execution and provider outcomes."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LearningRecord:
    """Execution outcome used to improve routing decisions."""

    prompt: str
    provider: str
    execution_time: float
    success: bool
    failures: list[str] = field(default_factory=list)
    retries: int = 0
    compile_results: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LearningEngine:
    """Record outcomes and compute provider performance scores."""

    def __init__(self, path: Path = Path("JNAS_AI_CORE/workspace/learning/history.json")) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.records = self._load()

    def record(self, record: LearningRecord) -> None:
        """Store a learning record."""
        with self._lock:
            self.records.append(record)
            self._save()

    def provider_stats(self) -> dict[str, dict[str, float]]:
        """Return success rate and average response time by provider."""
        with self._lock:
            stats: dict[str, dict[str, float]] = {}
            for provider in sorted({record.provider for record in self.records}):
                items = [record for record in self.records if record.provider == provider]
                successes = sum(1 for item in items if item.success)
                total_time = sum(item.execution_time for item in items)
                stats[provider] = {
                    "success_rate": successes / len(items) if items else 0.0,
                    "average_response_time": total_time / len(items) if items else 0.0,
                    "execution_count": float(len(items)),
                }
            return stats

    def rank_providers(self) -> list[tuple[str, float]]:
        """Rank providers using historical success and latency."""
        rankings = []
        for provider, stats in self.provider_stats().items():
            latency_penalty = min(stats["average_response_time"] / 60.0, 1.0)
            score = stats["success_rate"] * 0.8 + (1.0 - latency_penalty) * 0.2
            rankings.append((provider, score))
        return sorted(rankings, key=lambda item: item[1], reverse=True)

    def _load(self) -> list[LearningRecord]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            LearningRecord(
                prompt=item["prompt"],
                provider=item["provider"],
                execution_time=float(item["execution_time"]),
                success=bool(item["success"]),
                failures=list(item.get("failures", [])),
                retries=int(item.get("retries", 0)),
                compile_results=item.get("compile_results", ""),
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in data
        ]

    def _save(self) -> None:
        data = []
        for record in self.records:
            item = asdict(record)
            item["created_at"] = record.created_at.isoformat()
            data.append(item)
        self.path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
