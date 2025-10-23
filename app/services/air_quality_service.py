import os
import httpx

from app.models.db.weather import AirQuality # to be fixed

OPENAQ_URL = "https://api.openaq.org/v3/measurements"
API_KEY = os.getenv("OPENAQ_API_KEY", "e606a673d174e3126259f4c26bd3dd2e1b442de9b1aa5fa574f58348d55d3b14")

async def fetch_air_quality(city: str, date: str, country: str = None) -> AirQuality:
    params = {
        "city": city,
        "date_from": date,
        "date_to": date,
        "limit": 10
    }
    if country:
        params["country"] = country
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENAQ_URL, params=params, headers=headers)
        data = response.json()
        results = data.get("results", [])
        measurements = [r for r in results if "value" in r and "parameter" in r]
        if measurements:
            pm_values = [m["value"] for m in measurements if m["parameter"] in ["pm25", "pm10"]]
            if pm_values:
                aqi = int(sum(pm_values) / len(pm_values))
                description = "AQI based on PM2.5/PM10"
            else:
                values = [m["value"] for m in measurements]
                aqi = int(sum(values) / len(values)) if values else 0
                description = ", ".join([m["parameter"] for m in measurements])
        else:
            aqi = 0
            description = "No air quality data found for this city/date."
        return AirQuality(city=city, date=date, aqi=aqi, description=description, cached=False)
