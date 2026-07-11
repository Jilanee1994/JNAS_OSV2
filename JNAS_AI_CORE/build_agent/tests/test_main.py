from src.main import create_plan, main, run_build


def test_build_agent_creates_plan() -> None:
    assert "generate project" in create_plan("Build a scraper")


def test_build_agent_returns_successful_report() -> None:
    report = run_build("Build a scraper")
    assert report.status == "success"
    assert report.attempts == 1


def test_build_agent_cli_runs(capsys) -> None:
    assert main(["--goal", "Build a scraper"]) == 0
    assert "Build agent report" in capsys.readouterr().out
