from fastapi import APIRouter
from typing import List
from app.models.db.activity import Activity
from app.services.ticketmaster_service import (
    fetch_activities as fetch_ticketmaster_activities,
)
from app.services.weather_service import fetch_weather

router = APIRouter()
from app.routes.admin import admin_activities


@router.get("/activities", response_model=List[Activity])
async def get_activities(city: str, countryCode: str, date: str):
    ticketmaster_acts = await fetch_ticketmaster_activities(city, countryCode, date)
    custom_acts = [a for a in admin_activities if a.location == city and a.date == date]
    return ticketmaster_acts + custom_acts


@router.get("/activities/by-weather", response_model=List[Activity])
async def get_activities_by_weather(city: str, countryCode: str, date: str):
    weather = await fetch_weather(city, date)
    activities = await fetch_ticketmaster_activities(city, countryCode, date)
    if weather.condition.lower() in ["clear", "sunny"]:
        return [a for a in activities if not a.is_indoor or a.is_indoor is None]
    else:
        return [a for a in activities if a.is_indoor]
