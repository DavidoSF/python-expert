from fastapi.testclient import TestClient
from app.main import app

def test_vote_for_activities():
    client = TestClient(app)
    vote = {
        "user_id": 1,
        "activity_ranking": [2, 1, 3],  # Ranked list: activity 2 is first choice, 1 is second, 3 is third
        "activity_scores": [
            {"activity_id": 1, "user_id": 1, "score": 5},
            {"activity_id": 2, "user_id": 1, "score": 3}
        ]
    }
    response = client.post("/vote/", json=vote)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ok"
