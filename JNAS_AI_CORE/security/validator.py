"""Permission validation."""

from __future__ import annotations

from pathlib import Path

from .exceptions import PermissionError
from .policy import PermissionPolicy


class PermissionValidator:
    """Validate role permissions for actions."""

    def __init__(self, policy: PermissionPolicy | None = None) -> None:
        self.policy = policy or PermissionPolicy()

    def require(self, role: str, permission: str, path: Path | None = None) -> bool:
        """Require permission for a role and optional path."""
        if not self.policy.has_permission(role, permission):
            raise PermissionError(f"Role {role} lacks permission {permission}.")
        if path is not None and self.policy.requires_write_guard(path, permission) and role != "Admin":
            raise PermissionError(f"Protected path requires Admin permission: {path}")
        return True
