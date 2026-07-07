"""Role definitions."""

from __future__ import annotations

from .permissions import Permission


ROLE_PERMISSIONS = {
    "Admin": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE, Permission.NETWORK, Permission.FILESYSTEM},
    "Developer": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.FILESYSTEM},
    "Agent": {Permission.READ, Permission.WRITE, Permission.FILESYSTEM},
    "Worker": {Permission.READ, Permission.EXECUTE},
    "Sandbox": {Permission.READ},
}
