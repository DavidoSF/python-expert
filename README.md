# Weather Activity Recommender

A FastAPI-based service that recommends city activities based on weather conditions, air quality, and user preferences.

## Features

- **UC1-4**: Weather-based activity recommendations with personalization
- **UC5**: Administrators can enrich activity listings with custom activities
- **UC6**: External data sources configured via YAML configuration file
- Voting system for activities (with Condorcet method support planned)
- Air quality monitoring integration
- User profile management with interests and preferences

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure external APIs (see Configuration section below)

## Running the Application

### Development Server
```bash
python3.12 -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Configuration (UC6)

The application uses `config.yaml` for managing external data sources and settings.

### Configuration File Structure

```yaml
data_sources:
  weather:
    provider: "OpenWeatherMap"
    base_url: "https://api.openweathermap.org/data/2.5/weather"
    api_key: "your_key_here"
    timeout: 10
    
  air_quality:
    provider: "WAQI"
    base_url: "https://api.waqi.info/feed"
    api_key: "your_key_here"
    timeout: 10
    
  events:
    provider: "Ticketmaster"
    base_url: "https://app.ticketmaster.com/discovery/v2/events.json"
    api_key: "your_key_here"
    timeout: 10
    max_results: 100

recommendations:
  outdoor_conditions: ["clear", "sunny", "partly cloudy", "fair"]
  indoor_conditions: ["rain", "snow", "thunderstorm", "drizzle"]
  confidence_threshold: 0.7
```

### Environment Variables

API keys can be overridden using environment variables (takes precedence over config.yaml):

```bash
export OPENWEATHER_API_KEY="your_openweather_key"
export WAQI_API_KEY="your_waqi_key"
export TICKETMASTER_API_KEY="your_ticketmaster_key"
```

## API Endpoints

### Public Endpoints

- `GET /weather` - Get weather for a city and date
- `GET /air-quality` - Get air quality index
- `GET /activities/by-weather` - Get activities filtered by weather
- `POST /activities/personalized` - Get personalized activity recommendations
- `GET /weather-recommendation` - Get weather-based preference recommendation
- `POST /vote/` - Submit ranked activity vote (Condorcet method)
- `GET /vote/` - List all votes
- `GET /vote/result` - Get Condorcet voting results
- `GET /user/{user_id}` - Get user profile
- `POST /user/` - Create new user
- `PUT /user/{user_id}` - Update user profile
- `DELETE /user/{user_id}` - Delete user

### Voting System

The application uses **simple score-based voting** for activities:

**Vote for one or more activities:**
```json
{
  "votes": [
    {"user_id": 1, "activity_id": 5, "score": 9},
    {"user_id": 1, "activity_id": 3, "score": 7},
    {"user_id": 1, "activity_id": 8, "score": 10}
  ]
}
```

- **Score range**: 1-10 (10 = best, like it the most)
- **No duplicates**: Cannot vote for the same activity twice in one submission
- **Get ranking**: `GET /vote/ranking` returns activities sorted by average score

**Endpoints:**
- `POST /vote/` - Submit votes for activities
- `GET /vote/` - List all votes
- `GET /vote/activity/{activity_id}` - Get votes for specific activity with average
- `GET /vote/ranking` - Get all activities ranked by average score

**Example:**
```bash
# Vote for activities
curl -X POST "http://localhost:8000/vote/" \
  -H "Content-Type: application/json" \
  -d '{
    "votes": [
      {"user_id": 1, "activity_id": 5, "score": 9},
      {"user_id": 1, "activity_id": 3, "score": 7}
    ]
  }'

# Get ranking
curl "http://localhost:8000/vote/ranking"
```

### Admin Endpoints (UC5)

All admin endpoints require `admin_user_id` parameter with administrator role.

- `POST /admin/activity` - Add custom activity to enrich city listings
- `GET /admin/activities` - List combined Ticketmaster + custom activities
- `GET /admin/config` - View current configuration (UC6)

Example admin activity enrichment:
```bash
curl -X POST "http://localhost:8000/admin/activity" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Local Farmers Market",
    "type": "food",
    "location": "Paris",
    "is_indoor": false,
    "date": "2025-11-10",
    "description": "Weekly farmers market with local produce"
  }'
```

## Testing

Run all tests:
```bash
python3.12 -m pytest
```

Run with verbose output:
```bash
python3.12 -m pytest -vv
```

Run specific test file:
```bash
python -m pytest tests/test_activities.py -vv
```

## Architecture

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **httpx** - Async HTTP client
- **PyYAML** - Configuration management
- **pytest** - Testing framework

### Project Structure
```
app/
  ├── main.py              # FastAPI application entry point
  ├── models/
  │   ├── db/              # Domain models (Activity, User, Vote, Weather)
  │   └── response/        # API response models
  ├── routes/              # API endpoints (activities, admin, user, vote, weather)
  ├── services/            # Business logic and external API integration
  │   ├── config_service.py        # Configuration management (UC6)
  │   ├── activities_service.py    # Activity filtering & recommendations
  │   ├── weather_service.py       # OpenWeatherMap integration
  │   ├── air_quality_service.py   # WAQI integration
  │   ├── ticketmaster_service.py  # Ticketmaster Events API
  │   └── user_service.py          # User management
  └── data/
      └── users.json       # User data store
config.yaml                # Application configuration (UC6)
tests/                     # Test suite
```

## User Cases Implemented

- **UC1-4**: Activity recommendations based on weather, user preferences, and context
- **UC5**: Admin enrichment of activity listings via `/admin/activity` endpoint
- **UC6**: External data source configuration via `config.yaml` with YAML format
- User profile management with interests and activity preferences
- Weather-aware recommendation engine with configurable confidence thresholds
- Air quality monitoring integration

## Development Notes

- Default API keys are provided in `config.yaml` for testing (limited quota)
- For production: use environment variables to override API keys
- Admin access requires proper user role (use user_id of administrator)
- Voting system supports per-activity votes; Condorcet ranking planned





# sphinx

pip install -r requirements.txt
cd scripts/docs
make.bat html
cd _build/html
python -m http.server 8080