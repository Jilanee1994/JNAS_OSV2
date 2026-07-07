from __future__ import annotations

import argparse


def greet(name: str = "World") -> str:
    return f"Hello, {name}!"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hello application")
    parser.add_argument("--name", default="World")
    args = parser.parse_args(argv)
    print(greet(args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
