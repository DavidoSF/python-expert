"""
Service for managing and retrieving activities from all sources.
"""
from typing import List, Optional
from app.models.db.activity import Activity


def get_all_activity_ids() -> List[int]:
    """
    Get all known activity IDs from all sources (Ticketmaster + admin).
    Note: This is a snapshot of currently loaded activities.
    In a real app, you'd query a database.
    """
    from app.routes.admin import admin_activities
    
    # Get IDs from admin activities
    activity_ids = [a.id for a in admin_activities]
    
    # Note: Ticketmaster activities are fetched dynamically per city/date,
    # so we can't preload all possible IDs. We'll need to validate differently.
    return activity_ids


def activity_exists(activity_id: int) -> bool:
    """
    Check if an activity exists in admin activities.
    Note: For Ticketmaster activities, they're fetched dynamically,
    so this only checks admin activities for now.
    """
    from app.routes.admin import admin_activities
    return any(a.id == activity_id for a in admin_activities)


def get_activity_by_id(activity_id: int) -> Optional[Activity]:
    """Get an activity by ID from admin activities."""
    from app.routes.admin import admin_activities
    for activity in admin_activities:
        if activity.id == activity_id:
            return activity
    return None
