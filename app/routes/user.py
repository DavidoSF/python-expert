from fastapi import APIRouter
from app.models.db.user import User, UserRole
from datetime import date, datetime

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=User)
def get_profile():
    return User(
        id=1,
        username="alice",
        email="alice@example.com",
        first_name="Alice",
        last_name="Smith",
        birth_date=date(1990, 1, 1),
        gender="female",
        phone_number="+15551234567",
        country="US",
        city="Seattle",
        interests=["music", "hiking"],
        activity_preference="outdoor",
        role=UserRole.subscriber,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


