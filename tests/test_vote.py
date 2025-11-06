import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.admin import admin_activities
from app.models.db.activity import Activity, ActivityType
from app.services import vote_service


@pytest.fixture(autouse=True)
def setup_test_activities():
    """Set up test activities before each test."""
    admin_activities.clear()
    vote_service._VOTES.clear()

    admin_activities.extend(
        [
            Activity(
                id=5,
                name="Test Activity 5",
                description="Test",
                date="2024-03-15T14:00:00",
                location="Test City",
                type=ActivityType.cultural,
                is_indoor=False,
            ),
            Activity(
                id=3,
                name="Test Activity 3",
                description="Test",
                date="2024-03-15T14:00:00",
                location="Test City",
                type=ActivityType.sports,
                is_indoor=True,
            ),
            Activity(
                id=10,
                name="Test Activity 10",
                description="Test",
                date="2024-03-15T14:00:00",
                location="Test City",
                type=ActivityType.community,
                is_indoor=False,
            ),
            Activity(
                id=20,
                name="Test Activity 20",
                description="Test",
                date="2024-03-15T14:00:00",
                location="Test City",
                type=ActivityType.other,
                is_indoor=True,
            ),
        ]
    )

    yield

    admin_activities.clear()
    vote_service._VOTES.clear()


def test_vote_for_activities():
    """Test voting for activities with scores."""
    client = TestClient(app)
    vote = {
        "votes": [
            {"user_id": 1, "activity_id": 5, "score": 9},
            {"user_id": 1, "activity_id": 3, "score": 7},
        ]
    }
    response = client.post("/vote/", json=vote)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ok"
    assert data["votes_recorded"] == 2


def test_vote_with_duplicate_activity():
    """Test that voting for same activity twice is rejected."""
    client = TestClient(app)
    vote = {
        "votes": [
            {"user_id": 1, "activity_id": 5, "score": 9},
            {"user_id": 1, "activity_id": 5, "score": 7},
        ]
    }
    response = client.post("/vote/", json=vote)
    assert response.status_code == 422
    assert "same activity" in response.json()["detail"][0]["msg"].lower()


def test_vote_with_invalid_score():
    """Test that invalid scores (outside 1-10) are rejected."""
    client = TestClient(app)
    vote = {"votes": [{"user_id": 1, "activity_id": 5, "score": 15}]}
    response = client.post("/vote/", json=vote)
    assert response.status_code == 422


def test_get_activity_ranking():
    """Test getting activities ranked by average score."""
    client = TestClient(app)
    vote1 = {"votes": [{"user_id": 1, "activity_id": 10, "score": 9}]}
    vote2 = {"votes": [{"user_id": 2, "activity_id": 10, "score": 7}]}
    vote3 = {"votes": [{"user_id": 3, "activity_id": 20, "score": 10}]}

    client.post("/vote/", json=vote1)
    client.post("/vote/", json=vote2)
    client.post("/vote/", json=vote3)

    response = client.get("/vote/ranking")
    assert response.status_code == 200
    ranking = response.json()
    assert len(ranking) >= 2
    assert ranking[0]["activity_id"] == 20
    assert ranking[0]["average_score"] == 10.0
