"""Command entrypoint for JNAS Builder Agent."""

from __future__ import annotations

import sys

from JNAS_AI_CORE.Builder.builder_agent import main as legacy_main
from JNAS_AI_CORE.Builder.builder_v4 import main as v4_main


if __name__ == "__main__":
    if "--project" in sys.argv[1:]:
        sys.exit(v4_main())
    sys.exit(legacy_main())
