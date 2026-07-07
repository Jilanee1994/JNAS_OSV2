from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .job_search import export_jobs, sample_jobs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JOB_HUNTER CLI")
    parser.add_argument("--output", default="jobs.csv")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    args = build_parser().parse_args(argv)
    path = export_jobs(sample_jobs(), Path(args.output))
    print(f"Exported jobs to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
