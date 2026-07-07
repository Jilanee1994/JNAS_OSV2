"""Print latest JNAS AI Core session status."""

from __future__ import annotations

from JNAS_AI_CORE.session import SessionManager


def main() -> None:
    """Print the most recent session status."""
    manager = SessionManager()
    sessions = manager.session_history()
    if not sessions:
        print("No sessions found.")
        return

    session = sorted(sessions, key=lambda item: item.last_update)[-1]
    status = manager.get_status(session.session_id)
    for key, value in status.items():
        print(f"{key} : {value}")


if __name__ == "__main__":
    main()
