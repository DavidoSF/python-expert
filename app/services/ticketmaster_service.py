import os
import httpx
from typing import List

from app.models.db.activity import Activity, ActivityType

TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
API_KEY = os.getenv("TICKETMASTER_API_KEY", "Xkpv1HdAKWlmbtOPwqOpRv7RRDgUOtZU")

def _map_event_to_activity(event, date: str) -> Activity:
    return Activity(
        id=hash(event.get("id", "0")),
        name=event.get("name", "Event"),
        type=ActivityType.cultural,
        location=event.get("_embedded", {}).get("venues", [{}])[0].get("name", "Unknown"),
        is_indoor=True,
        date=date,
        description=event.get("info", "")
    )

async def fetch_activities(city: str, countryCode: str, date: str) -> List[Activity]:
    params = {
        "apikey": API_KEY,
        "countryCode": countryCode,
        "startDateTime": f"{date}T00:00:00Z",
        # "endDateTime": f"{date}T23:59:59Z",
        "includeTBD": "yes",
        "includeTBA": "yes",
        "size": 10,
        "city": city
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(TICKETMASTER_URL, params=params)
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        return [_map_event_to_activity(event, date) for event in events]
