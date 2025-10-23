from fastapi import APIRouter
from app.models import AirQuality
from app.services.air_quality_service import fetch_air_quality

router = APIRouter()

@router.get("/air-quality", response_model=AirQuality)
async def get_air_quality(city: str, date: str):
    return await fetch_air_quality(city, date)
