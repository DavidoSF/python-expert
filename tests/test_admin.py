from fastapi.testclient import TestClient
from app.main import app

def test_add_admin_activity_and_list():
    client = TestClient(app)
    activity = {
        "id": 100,
        "name": "Chess Tournament",
        "type": "sports",
        "location": "Paris",
        "is_indoor": True,
        "date": "2025-10-21",
        "description": "Indoor chess event"
    }
    # Add activity
    response = client.post("/admin/activity", json=activity)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chess Tournament"
    # List admin activities
    response = client.get("/admin/activities")
    assert response.status_code == 200
    activities = response.json()
    assert any(a["name"] == "Chess Tournament" for a in activities)
