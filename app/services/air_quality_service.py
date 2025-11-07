import httpx
from app.models.db.weather import AirQuality
from app.services.config_service import get_config

config = get_config()
air_quality_config = config.get_data_source_config('air_quality')

OPENAQ_URL = air_quality_config.get('base_url', 'https://api.waqi.info/feed')
API_KEY = air_quality_config.get('api_key', '')
TIMEOUT = air_quality_config.get('timeout', 10)

def get_aqi_category(aqi: int) -> str:
    """Return AQI category based on standard AQI ranges"""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

async def fetch_air_quality(city: str, date: str, country: str = None) -> AirQuality:
    city_query = f"{city}/{country}" if country else city
    url = f"{OPENAQ_URL}/{city_query}/"
    params = {"token": API_KEY}
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "ok" and "data" in data:
            aqi_data = data["data"]
            aqi = aqi_data.get("aqi", 0)
            category = get_aqi_category(aqi)
            
            pollutants = []
            iaqi = aqi_data.get("iaqi", {})
            
            pollutant_map = {
                "pm25": "PM2.5",
                "pm10": "PM10",
                "o3": "O₃",
                "no2": "NO₂",
                "so2": "SO₂",
                "co": "CO"
            }
            
            for pollutant_key, display_name in pollutant_map.items():
                if pollutant_key in iaqi:
                    value = iaqi[pollutant_key].get('v', 0)
                    pollutants.append(f"{display_name}: {value}")
            
            description = ", ".join(pollutants) if pollutants else f"Overall AQI: {aqi}"
        else:
            aqi = 0
            category = None
            description = "No air quality data found for this city/date."
        
        return AirQuality(city=city, date=date, aqi=aqi, category=category, description=description, cached=False)
