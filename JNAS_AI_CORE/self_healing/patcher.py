#!/usr/bin/env python3
"""
JNAS Auto Patch Engine
Version : 1.0

Usage:

python scripts/auto_patch.py \
    JNAS_AI_CORE/self_healing/patcher.py \
    apply_patch \
    patch.txt
"""

from pathlib import Path
import shutil
import re
import subprocess
import sys


def backup(file: Path):
    bak = file.with_suffix(file.suffix + ".bak")
    shutil.copy2(file, bak)
    print(f"[OK] Backup -> {bak}")


def restore(file: Path):
    bak = file.with_suffix(file.suffix + ".bak")
    if bak.exists():
        shutil.copy2(bak, file)
        print("[ROLLBACK] Restored backup")


def extract_function(text: str, func_name: str):
    pattern = (
        rf"(^\s*def\s+{func_name}\s*\(.*?(?=^\s*def\s+|^\s*class\s+|\Z))"
    )

    m = re.search(pattern, text, re.M | re.S)

    if not m:
        raise RuntimeError(f"{func_name} not found")

    return m.span()


def main():

    if len(sys.argv) != 4:
        print(
            "Usage:\n"
            "python auto_patch.py file.py function patch.txt"
        )
        sys.exit(1)

    file = Path(sys.argv[1])
    function = sys.argv[2]
    patch_file = Path(sys.argv[3])

    source = file.read_text(encoding="utf-8")
    replacement = patch_file.read_text(encoding="utf-8")

    backup(file)

    try:

        start, end = extract_function(source, function)

        new_source = (
            source[:start]
            + replacement
            + "\n"
            + source[end:]
        )

        file.write_text(new_source, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(file),
            ]
        )

        if result.returncode != 0:
            raise RuntimeError("Compilation failed")

        print("[SUCCESS] Patch applied.")

    except Exception as e:

        print(e)

        restore(file)

        sys.exit(1)


if __name__ == "__main__":
    main()