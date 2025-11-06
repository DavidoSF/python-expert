from fastapi.testclient import TestClient
from app.main import app

def test_vote_for_activities():
    client = TestClient(app)
    votes = [
        {"activity_id": 1, "user_id": 1, "score": 5},
        {"activity_id": 2, "user_id": 1, "score": 3}
    ]
    response = client.post("/vote", json=votes)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["activity_id"] == 1
    assert data[1]["score"] == 3
