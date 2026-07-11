import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

sys.path.insert(0, "../src")

from main import get_weather, main


class TestMain(unittest.TestCase):
    
    @patch('requests.get')
    def test_get_weather(self, mock_get):
        city = "London"
        api_response = {
            'weather': [{'description': 'Clear sky'}],
            'main': {'temp': 23}
        }
        
        mock_get.return_value.json.return_value = api_response
        
        get_weather(city)
        output = StringIO()
        sys.stdout = output
        main([f"--city={city}"])
        sys.stdout = sys.__stdout__
        
        expected_output = "Weather: Clear sky\nTemperature: 23.0°C\n"
        
        self.assertEqual(output.getvalue(), expected_output)


if __name__ == "__main__":
    unittest.main()
