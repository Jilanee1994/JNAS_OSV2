import csv

from src.job_search import Job, export_jobs, sample_jobs
from src.main import main


def test_job_model() -> None:
    job = Job("Engineer", "JNAS", "Remote", "https://example.com")
    assert job.title == "Engineer"


def test_csv_export(tmp_path) -> None:
    output = export_jobs(sample_jobs(), tmp_path / "jobs.csv")
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert rows and rows[0]["company"] == "JNAS"


def test_cli_runs(tmp_path, capsys) -> None:
    output = tmp_path / "jobs.csv"
    assert main(["--output", str(output)]) == 0
    assert output.exists()
    assert "Exported jobs" in capsys.readouterr().out
