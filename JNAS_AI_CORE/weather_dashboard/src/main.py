from __future__ import annotations

import argparse


FORECASTS = {
    "london": {"temperature": 18, "condition": "Cloudy"},
    "mumbai": {"temperature": 31, "condition": "Humid"},
    "new york": {"temperature": 24, "condition": "Clear"},
}


def get_forecast(city: str) -> dict[str, object]:
    key = city.strip().lower()
    return FORECASTS.get(key, {"temperature": 22, "condition": "Mild"})


def format_forecast(city: str) -> str:
    forecast = get_forecast(city)
    return f"Weather dashboard for {city}: {forecast['temperature']}C and {forecast['condition']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weather dashboard CLI")
    parser.add_argument("--city", default="London")
    args = parser.parse_args(argv)
    print(format_forecast(args.city))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
