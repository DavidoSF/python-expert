from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.db.activity import Activity
from app.services.ticketmaster_service import fetch_activities as fetch_ticketmaster_activities
from app.services import user_service
from app.models.db.user import UserRole
from app.services.config_service import get_config


router = APIRouter(prefix="/admin", tags=["admin"])

# In-memory admin-added activities
admin_activities: List[Activity] = []


@router.post("/activity", response_model=Activity)
def add_activity(activity: Activity):
    admin_activities.append(activity)
    return activity


@router.get("/activities", response_model=List[Activity])
async def list_admin_activities(
    city: str,
    countryCode: str,
    date: str,
    admin_user_id: int,
):
    """Return combined Ticketmaster events and admin-added activities for a city/date.

    This endpoint requires the requesting user to be an administrator. For demo purposes
    the caller must supply `admin_user_id` (in production use proper auth).
    """
    user_record = user_service.get_user_by_id(admin_user_id)
    if not user_record or user_record.get("role") != UserRole.administrator.value:
        raise HTTPException(status_code=403, detail="Administrator privileges required")

    ticketmaster_acts = await fetch_ticketmaster_activities(city, countryCode, date)
    custom_acts = [a for a in admin_activities if getattr(a, "location", None) == city and getattr(a, "date", None) == date]

    return ticketmaster_acts + custom_acts


@router.get("/config", response_model=Dict[str, Any])
def get_configuration(admin_user_id: int):
    """View current application configuration.
    
    Requires administrator privileges. Returns the full configuration including
    data source settings, recommendation parameters, etc.
    
    UC6: View configuration management.
    """
    user_record = user_service.get_user_by_id(admin_user_id)
    if not user_record or user_record.get("role") != UserRole.administrator.value:
        raise HTTPException(status_code=403, detail="Administrator privileges required")
    
    config = get_config()
    return {
        "app": config.get("app", {}),
        "data_sources": {
            "weather": config.get_data_source_config("weather"),
            "air_quality": config.get_data_source_config("air_quality"),
            "events": config.get_data_source_config("events"),
        },
        "recommendations": config.get_recommendation_config(),
        "activities": config.get("activities", {}),
    }

