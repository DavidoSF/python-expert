from fastapi import APIRouter
from app.models import Weather
from app.services.weather_service import fetch_weather

router = APIRouter()

@router.get("/weather", response_model=Weather)
async def get_weather(city: str, date: str):
    return await fetch_weather(city, date)


