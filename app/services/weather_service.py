import os
import httpx

from app.models.response.weather_response import WeatherResponse

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OPENWEATHER_API_KEY", "b2acb1abb1a3e05cfd68fdb6eb4d95cc")

async def fetch_weather(city: str, date: str) -> WeatherResponse:
    """
    
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENWEATHERMAP_URL, params=params)
        data = response.json()
        print('data=', data)
        temperature = data.get("main", {}).get("temp", 0.0)
        condition = data.get("weather", [{}])[0].get("main", "Unknown")
        return WeatherResponse(city=city, date=date, temperature=temperature, condition=condition, cached=False)