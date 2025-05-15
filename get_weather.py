import requests

def get_weather(city_name, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    try:
        return data['weather'][0]['description'], data['main']['temp']
    except:
        return "Weather data unavailable", "N/A"
