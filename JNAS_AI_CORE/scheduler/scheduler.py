"""Persistent autonomous OS scheduler."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone

from JNAS_AI_CORE.task_queue import QueuedTask, TaskQueue

from .job import ScheduledJob
from .store import ScheduleStore


class Scheduler:
    """Schedule one-time, recurring, cron-like, daily, and weekly work."""

    def __init__(self, task_queue: TaskQueue | None = None, store: ScheduleStore | None = None) -> None:
        self.task_queue = task_queue or TaskQueue()
        self.store = store or ScheduleStore()
        self._lock = threading.RLock()
        self._jobs: dict[str, ScheduledJob] = {job.job_id: job for job in self.store.load()}

    def schedule_once(self, name: str, task_type: str, run_at: datetime, payload: dict | None = None) -> ScheduledJob:
        """Schedule a one-time job."""
        return self._add_job(ScheduledJob(name=name, task_type=task_type, payload=payload or {}, run_at=run_at))

    def schedule_recurring(self, name: str, task_type: str, interval_seconds: int, payload: dict | None = None) -> ScheduledJob:
        """Schedule a recurring interval job."""
        return self._add_job(ScheduledJob(name=name, task_type=task_type, payload=payload or {}, interval_seconds=interval_seconds))

    def schedule_daily(self, name: str, task_type: str, hour: int, minute: int = 0, payload: dict | None = None) -> ScheduledJob:
        """Schedule a daily job."""
        now = datetime.now(timezone.utc)
        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_at <= now:
            run_at += timedelta(days=1)
        return self.schedule_recurring(name, task_type, 86400, payload={**(payload or {}), "daily": True, "run_at": run_at.isoformat()})

    def schedule_weekly(self, name: str, task_type: str, weekday: int, hour: int, payload: dict | None = None) -> ScheduledJob:
        """Schedule a weekly job where Monday is 0."""
        now = datetime.now(timezone.utc)
        days = (weekday - now.weekday()) % 7
        run_at = now.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=days)
        if run_at <= now:
            run_at += timedelta(days=7)
        return self._add_job(ScheduledJob(name=name, task_type=task_type, payload=payload or {}, run_at=run_at, interval_seconds=604800))

    def tick(self) -> list[QueuedTask]:
        """Enqueue due jobs and recover missed work."""
        now = datetime.now(timezone.utc)
        queued = []
        with self._lock:
            for job in self._jobs.values():
                if not job.enabled or job.run_at > now:
                    continue
                queued_task = QueuedTask(task_type=job.task_type, payload=job.payload, priority=job.payload.get("priority", 100))
                self.task_queue.enqueue(queued_task)
                queued.append(queued_task)
                job.last_run = now
                if job.interval_seconds:
                    while job.run_at <= now:
                        job.run_at += timedelta(seconds=job.interval_seconds)
                        if job.run_at <= now:
                            job.missed_runs += 1
                else:
                    job.enabled = False
            self.store.save(list(self._jobs.values()))
        return queued

    def recover_missed_jobs(self) -> list[QueuedTask]:
        """Recover jobs missed while the process was down."""
        self.task_queue.recover_running()
        return self.tick()

    def list_jobs(self) -> list[ScheduledJob]:
        """List configured jobs."""
        with self._lock:
            return list(self._jobs.values())

    def _add_job(self, job: ScheduledJob) -> ScheduledJob:
        with self._lock:
            self._jobs[job.job_id] = job
            self.store.save(list(self._jobs.values()))
        return job
