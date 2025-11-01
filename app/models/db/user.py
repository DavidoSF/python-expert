from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import date, datetime

class UserRole(str, Enum):
    subscriber = "subscriber"
    administrator = "administrator"

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = []
    activity_preference: Optional[str] = Field(
        default="either",
        description="Preferred activity location: 'indoor', 'outdoor' or 'either'"
    )
    role: str = "subscriber"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None