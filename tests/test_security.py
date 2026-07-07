"""Tests for permission system."""

from __future__ import annotations

from JNAS_AI_CORE.security import Permission, PermissionError, PermissionPolicy, PermissionValidator


def test_role_permission() -> None:
    validator = PermissionValidator()

    assert validator.require("Developer", Permission.WRITE) is True


def test_protected_path_requires_admin(tmp_path) -> None:
    protected = tmp_path / "protected"
    protected.mkdir()
    validator = PermissionValidator(PermissionPolicy([protected]))

    try:
        validator.require("Developer", Permission.WRITE, protected / "file.py")
    except PermissionError:
        pass
    else:
        raise AssertionError("Protected write should require Admin permission.")

    assert validator.require("Admin", Permission.WRITE, protected / "file.py") is True
