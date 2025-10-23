from fastapi import APIRouter
from app.models.response.weather_response import WeatherResponse
from app.services.weather_service import fetch_weather

router = APIRouter()

@router.get("/weather", response_model=WeatherResponse)
async def get_weather(city: str, date: str):
    return await fetch_weather(city, date)
