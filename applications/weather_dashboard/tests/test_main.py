from src.main import format_forecast, get_forecast, main


def test_get_forecast_contains_temperature() -> None:
    forecast = get_forecast("London")
    assert forecast["temperature"] == 18


def test_format_forecast_mentions_weather_dashboard() -> None:
    assert "Weather dashboard" in format_forecast("Mumbai")


def test_weather_dashboard_cli_runs(capsys) -> None:
    assert main(["--city", "London"]) == 0
    assert "Weather dashboard" in capsys.readouterr().out
