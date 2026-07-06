"""Permission policy."""

from __future__ import annotations

from pathlib import Path

from .permissions import Permission
from .roles import ROLE_PERMISSIONS


class PermissionPolicy:
    """Simple role and protected-path permission policy."""

    def __init__(self, protected_paths: list[Path] | None = None) -> None:
        self.protected_paths = [Path(path).resolve() for path in (protected_paths or [])]

    def has_permission(self, role: str, permission: str) -> bool:
        """Return whether a role has a permission."""
        return permission in ROLE_PERMISSIONS.get(role, set())

    def is_protected(self, path: Path) -> bool:
        """Return whether a path is protected."""
        resolved = Path(path).resolve()
        return any(resolved == protected or protected in resolved.parents for protected in self.protected_paths)

    def requires_write_guard(self, path: Path, permission: str) -> bool:
        """Return whether an operation should be guarded."""
        return permission in {Permission.WRITE, Permission.DELETE} and self.is_protected(path)
