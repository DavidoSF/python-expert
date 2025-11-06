from fastapi.testclient import TestClient
from app.main import app

def test_personalized_activities():
    """Test personalized activities endpoint (uses hardcoded user profile)."""
    client = TestClient(app)
    
    response = client.post(
        "/activities/personalized", 
        params={"city": "Paris", "countryCode": "FR", "date": "2025-11-01", "max_results": 10}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_weather_recommendation():
    client = TestClient(app)
    response = client.get("/weather-recommendation", params={"city": "Paris", "date": "2025-11-01"})
    assert response.status_code == 200
    data = response.json()
    assert "weather" in data
    assert "recommended_preference" in data
    assert "confidence" in data
    assert "reasoning" in data

def test_activities_by_weather_with_user():
    client = TestClient(app)
    response = client.get(
        "/activities/by-weather", 
        params={
            "city": "Paris", 
            "countryCode": "FR", 
            "date": "2025-11-01",
            "weather_preference": "outdoor",
            "max_results": 5
        }
    )
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, list)
    assert len(activities) <= 5