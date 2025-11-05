from fastapi import APIRouter
from app.models.db.user import User, UserRole, UserCreate, UserUpdate
from datetime import date, datetime, timezone
from fastapi import HTTPException, Response
from app.services import user_service
import os
from typing import Optional
from fastapi import Header

router = APIRouter(prefix="/user", tags=["user"])

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
    # Use Pydantic v2 API
    data = user.model_dump()
    data.pop("id", None)
    created = user_service.create_user(data)
    return User(**created)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate):
    """Update an existing user in the session store."""
    # Only include fields that were actually provided in the request body
    # Use Pydantic v2 API
    data = user.model_dump(exclude_unset=True)
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
    # Return an explicit empty response for 204 so no JSON content-type is set
    return Response(status_code=204)


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
    # Return explicit empty response for 204 to avoid application/json content-type
    return Response(status_code=204)


