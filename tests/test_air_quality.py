from fastapi.testclient import TestClient
from app.main import app

def test_get_air_quality():
    client = TestClient(app)
    response = client.get("/air-quality", params={"city": "Paris", "date": "2025-10-21"})
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert data["date"] == "2025-10-21"
    assert "aqi" in data
    assert "description" in data
