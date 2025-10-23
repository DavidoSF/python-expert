from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UserRole(str, Enum):
    subscriber = "subscriber"
    administrator = "administrator"

class User(BaseModel):
    id: int
    name: str
    role: UserRole

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

class Weather(BaseModel):
    city: str
    date: str
    temperature: float
    condition: str
    cached: bool = False

class AirQuality(BaseModel):
    city: str
    date: str
    aqi: int
    description: Optional[str] = None
    cached: bool = False

class ActivityVote(BaseModel):
    user_id: int
    activity_id: int
    score: int

class Vote(BaseModel):
    user_id: int
    activity_ranking: List[int]
    activity_scores: Optional[List[ActivityVote]] = None
