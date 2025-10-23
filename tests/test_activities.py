from fastapi.testclient import TestClient
from app.main import app

def test_get_activities():
    client = TestClient(app)
    response = client.get("/activities", params={"city": "Paris", "countryCode": "FR", "date": "2025-10-21"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_activities_by_weather():
    client = TestClient(app)
    response = client.get("/activities/by-weather", params={"city": "Paris", "countryCode": "FR", "date": "2025-10-21"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
