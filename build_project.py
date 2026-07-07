"""Command entrypoint for JNAS Builder Agent."""

from __future__ import annotations

import sys

from JNAS_AI_CORE.Builder.builder_agent import main as legacy_main
from JNAS_AI_CORE.Builder.builder_v4 import main as v4_main


if __name__ == "__main__":
    args = sys.argv[1:]
    v4_flags = {"--project", "--provider", "--milestone", "--output"}
    if not args or args[0].startswith("-") or any(arg in v4_flags for arg in args):
        sys.exit(v4_main())
    sys.exit(legacy_main())
