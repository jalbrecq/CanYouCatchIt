import requests
from config import weather_api_token

url = "http://api.openweathermap.org/data/2.5/weather?q=Brussels,be&APPID=" + weather_api_token

response = requests.request("GET", url, headers={}, data={})

print(response.json()['weather'])