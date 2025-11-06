from typing import List, Optional, Dict, Any

# algorithm:
# if weather is sunny/clear -> return outdoor activities
from app.models.db.activity import Activity
from app.services.ticketmaster_service import (
    fetch_activities as fetch_ticketmaster_activities,
)
from app.services.weather_service import fetch_weather

# get activities based on weather
from typing import List, Optional, Dict, Any, Tuple
from datetime import date as date_class

from app.models.db.activity import Activity, ActivityType
from app.models.db.user import User
from app.services.ticketmaster_service import (
    fetch_activities as fetch_ticketmaster_activities,
)
from app.services.weather_service import fetch_weather
from app.services.config_service import get_config
from app.services.vote_service import list_votes

config = get_config()
rec_config = config.get_recommendation_config()

OUTDOOR_WEATHER_CONDITIONS = rec_config.get(
    "outdoor_conditions", ["clear", "sunny", "partly cloudy", "fair"]
)
INDOOR_WEATHER_CONDITIONS = rec_config.get(
    "indoor_conditions",
    ["rain", "snow", "thunderstorm", "drizzle", "cloudy", "overcast", "fog", "mist"],
)
CONFIDENCE_THRESHOLD = rec_config.get("confidence_threshold", 0.7)


def get_admin_activities() -> List[Activity]:
    """Get admin-added activities from the admin module."""
    from app.routes.admin import admin_activities

    return admin_activities


from app.services.recommendation_service import get_collaborative_recommendations

OUTDOOR_WEATHER_CONDITIONS = ["clear", "sunny", "partly cloudy", "fair"]
INDOOR_WEATHER_CONDITIONS = [
    "rain",
    "snow",
    "thunderstorm",
    "drizzle",
    "cloudy",
    "overcast",
    "fog",
    "mist",
]


async def fetch_activities_by_weather(
    city: str,
    countryCode: str,
    date: str,
    user: Optional[User] = None,
    weather_preference: Optional[str] = "auto",  # "auto", "indoor", "outdoor", "all"
    activity_types: Optional[List[ActivityType]] = None,
    max_results: Optional[int] = None,
    custom_weather_mapping: Optional[Dict[str, str]] = None,
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

    admin_acts = get_admin_activities()
    custom_acts = [
        a
        for a in admin_acts
        if getattr(a, "location", None) == city and getattr(a, "date", None) == date
    ]
    activities.extend(custom_acts)

    print("activities: ", activities)
    print("user: ", user)
    if temperature_range and hasattr(weather, "temperature"):
        min_temp, max_temp = temperature_range
        if not (min_temp <= weather.temperature <= max_temp):
            return []

    if weather_preference == "auto":
        if user and user.activity_preference and user.activity_preference != "either":
            preference = user.activity_preference
        else:
            if custom_weather_mapping:
                preference = custom_weather_mapping.get(
                    weather.condition.lower(), "indoor"
                )
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
    if activity_types is None and user and user.interests:
        activity_types = _map_interests_to_activity_types(user.interests)

    print("activitiy_types: ", activity_types)
    user_age = None
    if user and user.birth_date:
        today = date_class.today()
        user_age = (
            today.year
            - user.birth_date.year
            - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
        )

    print("Age: ", user_age)
    filtered_activities = []

    for activity in activities:
        if activity_types and activity.type not in activity_types:
            print("print 1")
            continue

        if preference == "all":
            print("print 2")
            pass
        elif preference == "outdoor":
            if activity.is_indoor:
                continue
        elif preference == "indoor":
            print("in door")
            if not activity.is_indoor:
                print("Skipping")
                continue

        if user:
            if user_age is not None:
                if not _is_age_appropriate(activity, user_age):
                    continue

            if user.gender:
                if not _is_gender_appropriate(activity, user.gender):
                    continue

            if user.city and user.city.lower() != city.lower():
                pass

        filtered_activities.append(activity)

    print("filtered_activities: ", filtered_activities)
    if user:
        filtered_activities = _score_and_sort_activities(
            filtered_activities, user, weather
        )

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

    return mapped_types if mapped_types else list(ActivityType)


def _is_age_appropriate(activity: Activity, age: int) -> bool:
    """Check if activity is appropriate for user's age."""
    if age < 13:
        return "family" in activity.name.lower() or "kids" in activity.name.lower()
    elif age < 18:
        excluded_keywords = ["casino", "bar", "nightclub", "adult"]
        return not any(
            keyword in activity.name.lower() for keyword in excluded_keywords
        )
    else:
        return True


def _is_gender_appropriate(activity: Activity, gender: str) -> bool:
    """Check if activity matches gender preferences (if any)."""

    return True


def _score_and_sort_activities(
    activities: List[Activity], user: User, weather
) -> List[Activity]:
    """Score and sort activities based on user preferences and context."""
    scored_activities = []

    for activity in activities:
        score = 0.0

        score += 1.0

        if user.interests:
            for interest in user.interests:
                if (
                    interest.lower() in activity.name.lower()
                    or interest.lower() in (activity.description or "").lower()
                ):
                    score += 2.0

        user_activity_types = _map_interests_to_activity_types(user.interests or [])
        if activity.type in user_activity_types:
            score += 1.5

        if user.activity_preference == "outdoor" and not activity.is_indoor:
            score += 1.0
        elif user.activity_preference == "indoor" and activity.is_indoor:
            score += 1.0

        if user.city and user.city.lower() == activity.location.lower():
            score += 0.5

        scored_activities.append((score, activity))

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
            "temperature": getattr(weather, "temperature", None),
        },
        "recommended_preference": None,
        "confidence": 0.0,
        "reasoning": "",
    }

    condition_lower = weather.condition.lower()

    if condition_lower in OUTDOOR_WEATHER_CONDITIONS:
        recommendation["recommended_preference"] = "outdoor"
        recommendation["confidence"] = (
            0.8 if "clear" in condition_lower or "sunny" in condition_lower else 0.6
        )
        recommendation["reasoning"] = (
            f"Weather is {weather.condition}, suitable for outdoor activities"
        )
    elif condition_lower in INDOOR_WEATHER_CONDITIONS:
        recommendation["recommended_preference"] = "indoor"
        recommendation["confidence"] = (
            0.9
            if any(bad in condition_lower for bad in ["rain", "storm", "snow"])
            else 0.7
        )
        recommendation["reasoning"] = (
            f"Weather is {weather.condition}, better to stay indoors"
        )
    else:
        recommendation["recommended_preference"] = "indoor"
        recommendation["confidence"] = 0.5
        recommendation["reasoning"] = (
            f"Unknown weather condition '{weather.condition}', defaulting to indoor activities"
        )

    return recommendation


async def fetch_activities_by_weather_ordered_by_votes(
    city: str,
    countryCode: str,
    date: str,
    user: Optional[User] = None,
    weather_preference: Optional[str] = "auto",
    activity_types: Optional[List[ActivityType]] = None,
    max_results: Optional[int] = None,
) -> List[Activity]:
    """
    Fetch activities filtered by weather conditions and order them by vote count.

    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        user: Optional user profile for personalized filtering
        weather_preference: "auto" (weather-based), "indoor", "outdoor", "all"
        activity_types: Optional list of activity types to filter by
        max_results: Optional maximum number of activities to return

    Returns:
        List of activities ordered by vote count (most votes first)
    """
    activities = await fetch_activities_by_weather(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        weather_preference=weather_preference,
        activity_types=activity_types,
    )

    if not activities:
        return []

    votes = list_votes()
    print("All votes: ", votes)

    activity_scores: Dict[int, Tuple[float, int]] = {}
    for activity in activities:
        activity_votes_list = [v for v in votes if v.get("activity_id") == activity.id]
        if activity_votes_list:
            avg_score = sum(v.get("score", 0) for v in activity_votes_list) / len(
                activity_votes_list
            )
            vote_count = len(activity_votes_list)
            activity_scores[activity.id] = (avg_score, vote_count)
        else:
            activity_scores[activity.id] = (0.0, 0)

    sorted_activities = sorted(
        activities,
        key=lambda x: (
            activity_scores.get(x.id, (0.0, 0))[0],
            activity_scores.get(x.id, (0.0, 0))[1],
        ),
        reverse=True,
    )

    if max_results and len(sorted_activities) > max_results:
        sorted_activities = sorted_activities[:max_results]

    return sorted_activities


async def suggest_personalized_activities(
    city: str,
    countryCode: str,
    date: str,
    user: User,
    weather_preference: Optional[str] = "auto",
    max_results: Optional[int] = 5,
) -> List[Activity]:
    """
    Suggest activities based on weather, user similarity, and collaborative filtering.

    This function combines:
    1. Weather-appropriate activities filtering
    2. Similar user preferences (collaborative filtering)
    3. Personal activity history and voting patterns

    Args:
        city: City name
        countryCode: Country code
        date: Date in ISO format
        user: User to get recommendations for
        weather_preference: Weather preference override
        max_results: Maximum number of activities to return

    Returns:
        List of recommended activities ordered by relevance
    """
    weather_filtered = await fetch_activities_by_weather(
        city=city,
        countryCode=countryCode,
        date=date,
        user=user,
        weather_preference=weather_preference,
    )

    if not weather_filtered:
        return []

    print("Weather filtered activities: ", weather_filtered)

    recommendations = get_collaborative_recommendations(
        user=user, current_activities=weather_filtered, max_recommendations=max_results
    )

    print("recommendations: ", recommendations)

    recommended_activities = [activity for activity, score in recommendations]

    return recommended_activities
