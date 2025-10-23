from pydantic import BaseModel
from typing import Optional

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