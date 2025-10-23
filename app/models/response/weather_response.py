from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    date: str
    temperature: float
    condition: str
    cached: bool = False