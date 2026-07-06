"""Tests for Session Manager."""

from __future__ import annotations

from JNAS_AI_CORE.session import SessionManager, SessionPersistence, SessionStatus


def make_manager(tmp_path):
    return SessionManager(persistence=SessionPersistence(tmp_path))


def test_create_and_resume_session(tmp_path) -> None:
    manager = make_manager(tmp_path)
    session = manager.create_session("AI File Organizer", "OrganizerWorker", ["Scan", "Move"])

    loaded = manager.resume_session(session.session_id)

    assert loaded.project_name == "AI File Organizer"
    assert loaded.status == SessionStatus.RUNNING


def test_stop_and_archive_session(tmp_path) -> None:
    manager = make_manager(tmp_path)
    session = manager.create_session("Project", "Worker")

    stopped = manager.stop_session(session.session_id)
    archived = manager.archive_session(session.session_id)

    assert stopped.status == SessionStatus.STOPPED
    assert archived.status == SessionStatus.ARCHIVED


def test_history_heartbeat_progress_checkpoint(tmp_path) -> None:
    manager = make_manager(tmp_path)
    session = manager.create_session("Project", "Worker", ["A", "B"])

    manager.beat(session.session_id)
    manager.update_progress(session.session_id, "B", ["A"], ["B"], eta="8 min")
    manager.add_checkpoint(session.session_id, "after-a", {"done": ["A"]})
    history = manager.session_history()
    status = manager.get_status(session.session_id)

    assert len(history) == 1
    assert status["Progress"] == "50%"
    assert status["Current Task"] == "B"
    assert manager.persistence.load(session.session_id).checkpoints[0].name == "after-a"


def test_crash_recovery_and_timeline(tmp_path) -> None:
    manager = make_manager(tmp_path)
    session = manager.create_session("Project", "Worker")

    recovered = manager.recover_crashed_sessions()

    assert recovered[0].session_id == session.session_id
    assert recovered[0].status == SessionStatus.STOPPED
    assert recovered[0].timeline


def test_warnings_errors_self_healing(tmp_path) -> None:
    manager = make_manager(tmp_path)
    session = manager.create_session("Project", "Worker")

    manager.record_warning(session.session_id, "slow")
    manager.record_error(session.session_id, "failed")
    updated = manager.record_self_healing_attempt(session.session_id)

    assert updated.self_healing_attempts == 1
    assert updated.warnings == ["slow"]
    assert updated.errors == ["failed"]
