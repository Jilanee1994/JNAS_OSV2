"""Command entrypoint for JNAS Builder Agent V1."""

from __future__ import annotations

import sys

from JNAS_AI_CORE.Builder.builder_agent import main


if __name__ == "__main__":
    sys.exit(main())
