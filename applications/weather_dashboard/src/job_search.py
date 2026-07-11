from requests import get
from bs4 import BeautifulSoup

def get_weather_data():
    url = "https://www.weather.com/"
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    weather_data = soup.find('div', {'class': 'CurrentConditions--phraseValue--2xXS0'}).text
    return f"Weather: {weather_data}"
