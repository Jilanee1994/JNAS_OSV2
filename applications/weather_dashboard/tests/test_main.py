from src.main import greet, main


def test_greet() -> None:
    assert greet("JNAS") == "Hello, JNAS!"


def test_main_runs(capsys) -> None:
    assert main(["--name", "JNAS"]) == 0
    assert "Hello, JNAS!" in capsys.readouterr().out
