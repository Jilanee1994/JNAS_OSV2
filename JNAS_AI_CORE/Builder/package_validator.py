"""Package and import validation for generated Builder projects."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PackageValidationResult:
    """Result of package layout and import validation."""

    success: bool
    package_name: str
    errors: list[str] = field(default_factory=list)
    repaired_files: list[Path] = field(default_factory=list)

    def to_message(self) -> str:
        """Render validation result details."""
        if self.success:
            return "Package validation passed."
        return "\n".join(f"- {error}" for error in self.errors)


class PackageValidator:
    """Validate generated projects can be imported without PYTHONPATH edits."""

    def validate_and_repair(self, project_root: Path, package_name: str) -> PackageValidationResult:
        """Repair simple import mismatches, then validate package importability."""
        repaired = self.repair_imports(project_root, package_name)
        errors = self._validate_package(project_root, package_name)
        errors.extend(self._validate_imports(project_root, package_name))
        errors.extend(self._validate_subprocess_imports(project_root, package_name))
        return PackageValidationResult(not errors, package_name, errors, repaired)

    def repair_imports(self, project_root: Path, package_name: str) -> list[Path]:
        """Repair common flat-import test mistakes before pytest."""
        repaired: list[Path] = []
        package_dir = project_root / package_name
        module_names = {path.stem for path in package_dir.glob("*.py") if path.name != "__init__.py"} if package_dir.exists() else set()
        for path in (project_root / "tests").rglob("test_*.py") if (project_root / "tests").exists() else []:
            original = path.read_text(encoding="utf-8")
            updated = original
            for module_name in module_names:
                updated = re.sub(
                    rf"(^\s*from\s+){re.escape(module_name)}(\s+import\s+)",
                    rf"\1{package_name}.{module_name}\2",
                    updated,
                    flags=re.MULTILINE,
                )
                updated = re.sub(
                    rf"(^\s*import\s+){re.escape(module_name)}(\s*$)",
                    rf"\1{package_name}.{module_name}\2",
                    updated,
                    flags=re.MULTILINE,
                )
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                repaired.append(path)
        return repaired

    def _validate_package(self, project_root: Path, package_name: str) -> list[str]:
        errors: list[str] = []
        package_dir = project_root / package_name
        if not package_dir.exists() or not package_dir.is_dir():
            errors.append(f"Package directory is missing: {package_name}")
        if not (package_dir / "__init__.py").exists():
            errors.append(f"Package __init__.py is missing: {package_name}/__init__.py")
        return errors

    def _validate_imports(self, project_root: Path, package_name: str) -> list[str]:
        errors: list[str] = []
        package_dir = project_root / package_name
        module_names = {path.stem for path in package_dir.glob("*.py") if path.name != "__init__.py"} if package_dir.exists() else set()
        for path in project_root.rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.level > 0:
                        continue
                    root_module = node.module.split(".", 1)[0]
                    if root_module in module_names:
                        errors.append(f"{path.relative_to(project_root)} imports flat module '{node.module}' instead of '{package_name}.{node.module}'.")
                    if root_module == package_name:
                        target = package_dir.joinpath(*node.module.split(".")[1:]).with_suffix(".py")
                        if len(node.module.split(".")) > 1 and not target.exists():
                            errors.append(f"{path.relative_to(project_root)} imports missing module '{node.module}'.")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_module = alias.name.split(".", 1)[0]
                        if root_module in module_names:
                            errors.append(f"{path.relative_to(project_root)} imports flat module '{alias.name}' instead of '{package_name}.{alias.name}'.")
        return errors

    def _validate_subprocess_imports(self, project_root: Path, package_name: str) -> list[str]:
        completed = subprocess.run(
            [sys.executable, "-c", f"import {package_name}"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            return []
        output = (completed.stderr or completed.stdout or "").strip()
        return [f"Package import failed for '{package_name}': {output}"]
