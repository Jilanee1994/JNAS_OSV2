import requests
from bs4 import BeautifulSoup

def get_weather_data(location):
    url = f"https://www.weather.com/weather/today/{location.lower().replace(' ', '')}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        current_temp = soup.find("span", {"data-testid": "TemperatureValue"}).text
        condition = soup.find("div", {"class": "CurrentConditions--tempValue--3a50n"}).text.strip()
        weather_data = f"Current Temperature in {location}: {current_temp}°F, Condition: {condition}"
    except Exception as e:
        return None
    
    return weather_data
