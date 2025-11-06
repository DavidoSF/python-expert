from pydantic import BaseModel, field_serializer
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
    
    # @field_serializer('date')
    # def serialize_date(self, value: str) -> str:
    #     """Format date to only show YYYY-MM-DD, removing time portion."""
    #     if 'T' in value:
    #         return value.split('T')[0]
    #     return value
