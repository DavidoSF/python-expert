# get activities based on weather
from typing import List

# algorithm:
# if weather is sunny/clear -> return outdoor activities
from app.models.db.activity import Activity
from app.services.ticketmaster_service import fetch_activities as fetch_ticketmaster_activities
from app.services.weather_service import fetch_weather

# get activities based on weather
from typing import List, Optional, Dict, Any

# algorithm:
# if weather is sunny/clear -> return outdoor activities
from app.models.db.activity import Activity, ActivityType
from app.services.ticketmaster_service import fetch_activities as fetch_ticketmaster_activities
from app.services.weather_service import fetch_weather

# Weather condition mappings for flexibility
OUTDOOR_WEATHER_CONDITIONS = ["clear", "sunny", "partly cloudy", "fair"]
INDOOR_WEATHER_CONDITIONS = ["rain", "snow", "thunderstorm", "drizzle", "cloudy", "overcast", "fog", "mist"]

async def fetch_activities_by_weather(
    city: str, 
    countryCode: str, 
    date: str,
    weather_preference: Optional[str] = "auto",  # "auto", "indoor", "outdoor", "all"
    activity_types: Optional[List[ActivityType]] = None,  # Filter by activity types
    max_results: Optional[int] = None,  # Limit number of results
    custom_weather_mapping: Optional[Dict[str, str]] = None,  # Custom weather -> preference mapping
    temperature_range: Optional[tuple] = None,  # (min_temp, max_temp) for filtering
) -> List[Activity]:
    """
    Fetch activities filtered by weather conditions with dynamic configuration.
    
    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        weather_preference: "auto" (weather-based), "indoor", "outdoor", "all"
        activity_types: List of activity types to filter by
        max_results: Maximum number of activities to return
        custom_weather_mapping: Custom mapping of weather conditions to preferences
        temperature_range: Tuple of (min_temp, max_temp) for temperature filtering
    
    Returns:
        List of filtered activities
    """
    weather = await fetch_weather(city, date)
    activities = await fetch_ticketmaster_activities(city, countryCode, date)

    # Apply temperature filtering if specified
    if temperature_range and hasattr(weather, 'temperature'):
        min_temp, max_temp = temperature_range
        if not (min_temp <= weather.temperature <= max_temp):
            return []  # No activities if temperature is out of range

    # Determine weather preference
    if weather_preference == "auto":
        # Use custom mapping if provided, otherwise use default logic
        if custom_weather_mapping:
            preference = custom_weather_mapping.get(weather.condition.lower(), "indoor")
        else:
            if weather.condition.lower() in OUTDOOR_WEATHER_CONDITIONS:
                preference = "outdoor"
            elif weather.condition.lower() in INDOOR_WEATHER_CONDITIONS:
                preference = "indoor"
            else:
                preference = "indoor"  # Default to indoor for unknown conditions
    else:
        preference = weather_preference

    filtered_activities = []
    
    for activity in activities:
        # Apply activity type filtering
        if activity_types and activity.type not in activity_types:
            continue
            
        # Apply weather-based filtering
        if preference == "all":
            filtered_activities.append(activity)
        elif preference == "outdoor":
            if not activity.is_indoor or activity.is_indoor is None:
                filtered_activities.append(activity)
        elif preference == "indoor":
            if activity.is_indoor:
                filtered_activities.append(activity)

    # Apply max results limit
    if max_results and len(filtered_activities) > max_results:
        filtered_activities = filtered_activities[:max_results]

    return filtered_activities

async def get_weather_recommendation(city: str, date: str) -> Dict[str, Any]:
    """
    Get weather-based activity recommendations with metadata.
    
    Returns:
        Dict containing weather info and recommendations
    """
    weather = await fetch_weather(city, date)
    
    recommendation = {
        "weather": {
            "condition": weather.condition,
            "temperature": getattr(weather, 'temperature', None),
        },
        "recommended_preference": None,
        "confidence": 0.0,
        "reasoning": ""
    }
    
    condition_lower = weather.condition.lower()
    
    if condition_lower in OUTDOOR_WEATHER_CONDITIONS:
        recommendation["recommended_preference"] = "outdoor"
        recommendation["confidence"] = 0.8 if "clear" in condition_lower or "sunny" in condition_lower else 0.6
        recommendation["reasoning"] = f"Weather is {weather.condition}, suitable for outdoor activities"
    elif condition_lower in INDOOR_WEATHER_CONDITIONS:
        recommendation["recommended_preference"] = "indoor"
        recommendation["confidence"] = 0.9 if any(bad in condition_lower for bad in ["rain", "storm", "snow"]) else 0.7
        recommendation["reasoning"] = f"Weather is {weather.condition}, better to stay indoors"
    else:
        recommendation["recommended_preference"] = "indoor"
        recommendation["confidence"] = 0.5
        recommendation["reasoning"] = f"Unknown weather condition '{weather.condition}', defaulting to indoor activities"
    
    return recommendation
