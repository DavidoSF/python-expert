import httpx
from typing import List
from app.models.db.activity import Activity, ActivityType
from app.services.config_service import get_config

# Load configuration
config = get_config()
events_config = config.get_data_source_config('events')

TICKETMASTER_URL = events_config.get('base_url', 'https://app.ticketmaster.com/discovery/v2/events.json')
API_KEY = events_config.get('api_key', '')
TIMEOUT = events_config.get('timeout', 10)
MAX_RESULTS = events_config.get('max_results', 100)

def _map_event_to_activity(event, date: str) -> Activity:
    print("dates: ", event.get("dates", {}))
    dates = event.get("dates", {})
    localDate = None
    if dates is not None:
        start = dates.get("start", {})
        print("start: ", start)
        if start is not None:
            localDate = start.get("localDate", "No date provided")
            print("localDate: ", localDate)
        
    return Activity(
        id=hash(event.get("id", "0")),
        name=event.get("name", "Event"),
        type=ActivityType.cultural,
        location=event.get("_embedded", {}).get("venues", [{}])[0].get("name", "Unknown"),
        is_indoor=True,
        date=localDate,
        description=event.get("info", "")
    )

async def fetch_activities(city: str, countryCode: str, date: str) -> List[Activity]:
    params = {
        "apikey": API_KEY,
        # "countryCode": countryCode,
        "startDateTime": f"{date}T00:00:00Z",
        "endDateTime": f"{date}T23:59:59Z",
        "includeTBD": "yes",
        "includeTBA": "yes",
        "size": min(10, MAX_RESULTS),
        "keyword": city
        # "city": city
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(TICKETMASTER_URL, params=params)
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        return [_map_event_to_activity(event, date) for event in events]
