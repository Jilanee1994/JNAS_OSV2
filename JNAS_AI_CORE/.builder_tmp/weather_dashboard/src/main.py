import argparse
from bs4 import BeautifulSoup
import requests
import sys


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_API_KEY&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if "weather" in data and "main" in data:
        weather_conditions = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        
        print(f"Weather: {weather_conditions}")
        print(f"Temperature: {temperature}°C")
    else:
        print("Failed to retrieve weather data.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Get weather forecast for a city.")
    parser.add_argument("--city", required=True, help="City name for weather forecast")
    
    args = parser.parse_args()
    
    get_weather(args.city)


if __name__ == "__main__":
    main()
