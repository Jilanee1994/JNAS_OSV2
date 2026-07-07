"""Repository health checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class RepositoryHealth:
    """Run lightweight repository health checks."""

    def compile_check(self, root: Path = Path("JNAS_AI_CORE")) -> dict[str, object]:
        """Run Python compile validation."""
        result = subprocess.run([sys.executable, "-m", "compileall", str(root)], capture_output=True, text=True, check=False)
        return {"success": result.returncode == 0, "output": (result.stdout + result.stderr).strip()}

    def git_status(self, root: Path = Path(".")) -> str:
        """Return git status if available."""
        result = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else "Git metadata unavailable."
