from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str
    url: str


def sample_jobs() -> list[Job]:
    return [
        Job("Python Developer", "JNAS", "Remote", "https://example.com/python"),
        Job("Automation Engineer", "JNAS", "Remote", "https://example.com/automation"),
    ]


def export_jobs(jobs: list[Job], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["title", "company", "location", "url"])
        writer.writeheader()
        for job in jobs:
            writer.writerow(job.__dict__)
    LOGGER.info("Exported %s jobs to %s", len(jobs), output_path)
    return output_path
