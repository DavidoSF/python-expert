from fastapi import APIRouter
from app.models import User, UserRole
from typing import List

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=User)
def get_profile():
    return User(id=1, name="Alice", role=UserRole.subscriber)


