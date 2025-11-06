from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ActivityType(str, Enum):
    cultural = "cultural"
    sports = "sports"
    community = "community"
    other = "other"

class Activity(BaseModel):
    id: int
    name: str
    type: ActivityType
    location: str
    is_indoor: bool
    date: str
    description: Optional[str] = None
