"""Dependency checking utilities."""

from __future__ import annotations

import importlib.util


class DependencyChecker:
    """Check whether optional runtime dependencies are installed."""

    def check(self, packages: list[str]) -> dict[str, bool]:
        """Return install status for package names."""
        return {package: importlib.util.find_spec(package) is not None for package in packages}
