from fastapi import APIRouter
from app.models.db.user import User, UserRole

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=User)
def get_profile():
    return User(id=1, name="Alice", role=UserRole.subscriber)


