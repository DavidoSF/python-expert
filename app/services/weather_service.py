import httpx
from app.models.response.weather_response import WeatherResponse
from app.services.config_service import get_config

config = get_config()
weather_config = config.get_data_source_config('weather')

OPENWEATHERMAP_URL = weather_config.get('base_url', 'https://api.openweathermap.org/data/2.5/weather')
API_KEY = weather_config.get('api_key', '')
TIMEOUT = weather_config.get('timeout', 10)

async def fetch_weather(city: str, date: str) -> WeatherResponse:
    """
    
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(OPENWEATHERMAP_URL, params=params)
        data = response.json()
        print('data=', data)
        temperature = data.get("main", {}).get("temp", 0.0)
        condition = data.get("weather", [{}])[0].get("main", "Unknown")
        return WeatherResponse(city=city, date=date, temperature=temperature, condition=condition, cached=False)