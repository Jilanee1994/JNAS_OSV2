"""Permission constants."""

from __future__ import annotations


class Permission:
    """Supported permission names."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    NETWORK = "network"
    FILESYSTEM = "filesystem"
