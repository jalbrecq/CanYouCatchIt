import requests

weather_api_token = 'e98872d0940b9785a1e048d5a5a599dd'
url = "http://api.openweathermap.org/data/2.5/weather?q=Brussels,be&APPID=" + weather_api_token

response = requests.request("GET", url, headers={}, data={})

print(response.json()['weather'])