from main import get_weather, main

def test_get_weather():
    weather_data = get_weather("London")
    assert weather_data["temperature"] == 15
    assert weather_data["conditions"] == "Sunny"

def test_main():
    import io
    import sys
    from unittest.mock import patch
    
    expected_output = "Temperature in London: 15°C\nConditions: Sunny\n"
    
    with patch("sys.argv", ["main.py", "London"]), \
         patch('sys.stdout', new_callable=io.StringIO) as stdout:
        main("London")
        
    assert stdout.getvalue() == expected_output
