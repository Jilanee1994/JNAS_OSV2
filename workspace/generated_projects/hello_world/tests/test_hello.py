from hello_world.hello import greet


def test_greet() -> None:
    assert greet() == "Hello, World!"
