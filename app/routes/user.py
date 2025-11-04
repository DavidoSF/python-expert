from fastapi import APIRouter
from app.models.db.user import User, UserRole, UserCreate, UserUpdate
from datetime import date, datetime
from fastapi import HTTPException
from app.services import user_service
import os
from typing import Optional
from fastapi import Header

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

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    """Return a user by id from the JSON data file; raises 404 if not found."""
    data = user_service.get_user_by_id(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**data)


@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """Create a new user in the session store (does not modify the original JSON file)."""
    data = user.dict()
    data.pop("id", None)
    created = user_service.create_user(data)
    return User(**created)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate):
    """Update an existing user in the session store."""
    # Only include fields that were actually provided in the request body
    data = user.dict(exclude_unset=True)
    data.pop("id", None)
    updated = user_service.update_user(user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**updated)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    """Delete a user from the session store."""
    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None


# Development-only endpoint: reset the in-memory user store to the original JSON.
# If you set the environment variable RESET_TOKEN, the request must include a matching
# header 'x-reset-token' to authorize the reset. Keep this disabled/guarded in prod.
RESET_TOKEN = os.getenv("RESET_TOKEN")


@router.post("/reset", status_code=204)
def reset_users(x_reset_token: Optional[str] = Header(None)):
    """Reset the in-memory users store from `app/data/users.json`.

    - If RESET_TOKEN env var is set, request must include header `x-reset-token` with that value.
    - This does not modify the JSON file on disk; it only resets the in-memory session store.
    """
    if RESET_TOKEN:
        if x_reset_token != RESET_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")
    user_service.reset_store()
    return None


