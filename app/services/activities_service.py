# get activities based on weather
from typing import List

# algorithm:
# if weather is sunny/clear -> return outdoor activities
from app.models.db.activity import Activity
from app.services.ticketmaster_service import fetch_activities as fetch_ticketmaster_activities
from app.services.weather_service import fetch_weather

# get activities based on weather
from typing import List, Optional, Dict, Any
from datetime import date as date_class

# algorithm:
# if weather is sunny/clear -> return outdoor activities
from app.models.db.activity import Activity, ActivityType
from app.models.db.user import User
from app.services.ticketmaster_service import fetch_activities as fetch_ticketmaster_activities
from app.services.weather_service import fetch_weather

# Weather condition mappings for flexibility
OUTDOOR_WEATHER_CONDITIONS = ["clear", "sunny", "partly cloudy", "fair"]
INDOOR_WEATHER_CONDITIONS = ["rain", "snow", "thunderstorm", "drizzle", "cloudy", "overcast", "fog", "mist"]

async def fetch_activities_by_weather(
    city: str, 
    countryCode: str, 
    date: str,
    user: Optional[User] = None,  # User profile for personalized filtering
    weather_preference: Optional[str] = "auto",  # "auto", "indoor", "outdoor", "all"
    activity_types: Optional[List[ActivityType]] = None,  # Filter by activity types
    max_results: Optional[int] = None,  # Limit number of results
    custom_weather_mapping: Optional[Dict[str, str]] = None,  # Custom weather -> preference mapping
    temperature_range: Optional[tuple] = None,  # (min_temp, max_temp) for filtering
) -> List[Activity]:
    """
    Fetch activities filtered by weather conditions and user preferences.
    
    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        user: User profile for personalized filtering
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
    print("activities: ", activities)
    print("user: ", user)
    # Apply temperature filtering if specified
    if temperature_range and hasattr(weather, 'temperature'):
        min_temp, max_temp = temperature_range
        if not (min_temp <= weather.temperature <= max_temp):
            return []  # No activities if temperature is out of range

    # Determine weather preference based on user or override
    if weather_preference == "auto":
        # Check user's activity preference first
        if user and user.activity_preference and user.activity_preference != "either":
            preference = user.activity_preference
        else:
            # Use custom mapping if provided, otherwise use default logic
            if custom_weather_mapping:
                preference = custom_weather_mapping.get(weather.condition.lower(), "indoor")
            else:
                preference = "all"
                # if weather.condition.lower() in OUTDOOR_WEATHER_CONDITIONS:
                #     preference = "outdoor"
                # elif weather.condition.lower() in INDOOR_WEATHER_CONDITIONS:
                #     preference = "indoor"
                # else:
                #     preference = "indoor"  # Default to indoor for unknown conditions
    else:
        preference = weather_preference
    print("USER PREFERENCE: ", preference)
    # Determine activity types to filter by
    if activity_types is None and user and user.interests:
        # Map user interests to activity types
        activity_types = _map_interests_to_activity_types(user.interests)

    print("activitiy_types: ", activity_types)
    # Calculate user age for age-appropriate filtering
    user_age = None
    if user and user.birth_date:
        today = date_class.today()
        user_age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))

    print("Age: ", user_age)
    filtered_activities = []
    
    for activity in activities:
        # Apply activity type filtering
        if activity_types and activity.type not in activity_types:
            print("print 1")
            continue

        # Apply weather-based filtering
        if preference == "all":
            print("print 2")
            pass  # Include all activities
        elif preference == "outdoor":
            if activity.is_indoor:
                continue  # Skip indoor activities
        elif preference == "indoor":
            print("in door")
            if not activity.is_indoor:
                print("Skipping")
                continue  # Skip outdoor activities
            
        # Apply user-specific filtering
        if user:
            # Age-based filtering (example: some activities might not be suitable for certain ages)
            if user_age is not None:
                if not _is_age_appropriate(activity, user_age):
                    continue
            
            # Gender-based filtering (if activity has gender preferences)
            if user.gender:
                if not _is_gender_appropriate(activity, user.gender):
                    continue
            
            # Location preference (if user prefers activities in their city)
            if user.city and user.city.lower() != city.lower():
                # User prefers activities in their home city, but we're searching elsewhere
                # This is just an example - you might want different logic
                pass

        filtered_activities.append(activity)

    print("filtered_activities: ", filtered_activities)
    # Apply personalized scoring and sorting
    if user:
        filtered_activities = _score_and_sort_activities(filtered_activities, user, weather)

    # Apply max results limit
    if max_results and len(filtered_activities) > max_results:
        filtered_activities = filtered_activities[:max_results]

    return filtered_activities

def _map_interests_to_activity_types(interests: List[str]) -> List[ActivityType]:
    """Map user interests to ActivityType enums."""
    interest_mapping = {
        "music": ActivityType.cultural,
        "art": ActivityType.cultural,
        "theater": ActivityType.cultural,
        "museum": ActivityType.cultural,
        "culture": ActivityType.cultural,
        "sports": ActivityType.sports,
        "fitness": ActivityType.sports,
        "football": ActivityType.sports,
        "basketball": ActivityType.sports,
        "running": ActivityType.sports,
        "community": ActivityType.community,
        "volunteer": ActivityType.community,
        "social": ActivityType.community,
        "cultural": ActivityType.cultural,
        "hiking": ActivityType.sports,
    }
    
    mapped_types = []
    for interest in interests:
        if interest.lower() in interest_mapping:
            activity_type = interest_mapping[interest.lower()]
            if activity_type not in mapped_types:
                mapped_types.append(activity_type)
    
    # If no specific mapping found, include all types
    return mapped_types if mapped_types else list(ActivityType)

def _is_age_appropriate(activity: Activity, age: int) -> bool:
    """Check if activity is appropriate for user's age."""
    # Example logic - you can expand this based on activity content
    if age < 13:
        # Child-friendly activities only
        return "family" in activity.name.lower() or "kids" in activity.name.lower()
    elif age < 18:
        # Teen-appropriate activities
        excluded_keywords = ["casino", "bar", "nightclub", "adult"]
        return not any(keyword in activity.name.lower() for keyword in excluded_keywords)
    else:
        # Adults can attend most activities
        return True

def _is_gender_appropriate(activity: Activity, gender: str) -> bool:
    """Check if activity matches gender preferences (if any)."""
    # Most activities are gender-neutral, but some might have specific audiences
    # This is a basic example - you might want more sophisticated logic
    
    # For now, assume all activities are appropriate for all genders
    # You could add specific filtering based on activity content/description
    return True

def _score_and_sort_activities(activities: List[Activity], user: User, weather) -> List[Activity]:
    """Score and sort activities based on user preferences and context."""
    scored_activities = []
    
    for activity in activities:
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Interest-based scoring
        if user.interests:
            for interest in user.interests:
                if interest.lower() in activity.name.lower() or \
                   interest.lower() in (activity.description or "").lower():
                    score += 2.0
        
        # Activity type preference scoring
        user_activity_types = _map_interests_to_activity_types(user.interests or [])
        if activity.type in user_activity_types:
            score += 1.5
        
        # Weather appropriateness scoring
        if user.activity_preference == "outdoor" and not activity.is_indoor:
            score += 1.0
        elif user.activity_preference == "indoor" and activity.is_indoor:
            score += 1.0
        
        # Location preference
        if user.city and user.city.lower() == activity.location.lower():
            score += 0.5
        
        scored_activities.append((score, activity))
    
    # Sort by score (highest first)
    scored_activities.sort(key=lambda x: x[0], reverse=True)
    
    return [activity for score, activity in scored_activities]

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
