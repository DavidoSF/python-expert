from fastapi import APIRouter, Body
from typing import List, Optional
from datetime import date, datetime
from app.models.db.activity import Activity
from app.models.db.user import User, UserRole
from app.routes.user import get_user
from app.services.ticketmaster_service import (
    fetch_activities as fetch_ticketmaster_activities,
)
from app.services.weather_service import fetch_weather

router = APIRouter()
from app.routes.admin import admin_activities
from app.services.activities_service import (
    fetch_activities_by_weather,
    fetch_activities_by_weather_ordered_by_votes,
    get_weather_recommendation,
    suggest_personalized_activities
)

@router.post("/activities/personalized", response_model=List[Activity])
async def get_personalized_activities(
    city: str,
    countryCode: str,
    date: Optional[str] = "2025-11-06",
    user_id: Optional[int] = 1,
    max_results: Optional[int] = 20,
):
    """
    Get personalized activities based on user profile and weather conditions.
    """
    
    user = get_user(user_id)
    
    if date is None:
        date = datetime.now().date().isoformat()

    return await fetch_activities_by_weather(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        max_results=max_results
    )

@router.get("/activities/recommended", response_model=List[Activity])
async def get_recommended_activities(
    city: str,
    countryCode: str,
    date: str,
    user_id: Optional[int] = 1,
    weather_preference: Optional[str] = "auto",
    max_results: Optional[int] = 5
):
    """
    Get personalized activity recommendations based on:
    - Weather conditions
    - Similar user preferences
    - User profile and interests
    - Activity voting history
    
    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        weather_preference: Optional weather preference ("auto", "indoor", "outdoor", "all")
        max_results: Maximum number of recommendations to return
    
    Returns:
        List of recommended activities ordered by relevance
    """
    user = get_user(user_id)
    
    recommended = await suggest_personalized_activities(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        weather_preference=weather_preference,
        max_results=max_results
    )
    
    return recommended

@router.get("/activities/by-votes", response_model=List[Activity])
async def get_activities_by_votes(
    city: str,
    countryCode: str,
    date: str,
    weather_preference: Optional[str] = "auto",
    user_id: Optional[int] = 1,
    max_results: Optional[int] = 20
):
    """
    Get activities filtered by weather conditions and ordered by vote count.
    
    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        weather_preference: Weather preference ("auto", "indoor", "outdoor", "all")
        max_results: Maximum number of activities to return
    
    Returns:
        List of activities ordered by vote count (most votes first)
    """
    user = get_user(user_id) 
    
    return await fetch_activities_by_weather_ordered_by_votes(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        weather_preference=weather_preference,
        max_results=max_results
    )

@router.get("/activities/by-weather", response_model=List[Activity])
async def get_activities_by_weather(
    city: str, 
    countryCode: str, 
    date: str,
    user_id: Optional[int] = None,
    weather_preference: Optional[str] = "auto",
    max_results: Optional[int] = None
):
    """
    Get activities filtered by weather conditions, optionally personalized for a user.
    """
    user = get_user(user_id) if user_id else None
    
    activities = await fetch_activities_by_weather(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        weather_preference=weather_preference,
        max_results=max_results
    )
    
    return activities

@router.get("/weather-recommendation")
async def get_weather_recommendation_endpoint(city: str, date: str):
    """
    Get weather-based activity recommendations with confidence scores.
    """
    return await get_weather_recommendation(city, date)
