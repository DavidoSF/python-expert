from fastapi import APIRouter
from typing import List
from app.models.db.activity import Activity


router = APIRouter(prefix="/admin", tags=["admin"])

admin_activities = []


@router.post("/activity", response_model=Activity)
def add_activity(activity: Activity):
    admin_activities.append(activity)
    return activity


@router.get("/activities", response_model=List[Activity])
def list_admin_activities():
    return admin_activities
