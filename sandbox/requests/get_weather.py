import requests

weather_api_token = 'Place_your_acces_token_here'
url = "http://api.openweathermap.org/data/2.5/weather?q=Brussels,be&APPID=" + weather_api_token

response = requests.request("GET", url, headers={}, data={})

print(response.json()['weather'])