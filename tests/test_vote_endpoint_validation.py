"""
Test vote endpoint validations
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.admin import admin_activities
from app.models.db.activity import Activity, ActivityType
from app.services import vote_service


@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data before each test."""
    admin_activities.clear()
    vote_service._VOTES.clear()
    
    admin_activities.append(
        Activity(
            id=100,
            name="Test Activity",
            description="Test",
            date="2024-03-15T14:00:00",
            location="Paris",
            type=ActivityType.cultural,
            is_indoor=True
        )
    )
    
    vote_service.add_vote({"user_id": 1, "activity_id": 100, "score": 9})
    vote_service.add_vote({"user_id": 2, "activity_id": 100, "score": 8})
    
    yield
    
    admin_activities.clear()
    vote_service._VOTES.clear()


client = TestClient(app)


def test_get_votes_for_nonexistent_activity():
    """Test that querying votes for non-existent activity returns 404."""
    response = client.get("/vote/activity/999")
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_get_votes_for_existing_activity():
    """Test that querying votes for existing activity succeeds."""
    response = client.get("/vote/activity/100")
    assert response.status_code == 200
    data = response.json()
    assert data["activity_id"] == 100
    assert data["total_votes"] == 2
    assert data["average_score"] == 8.5


def test_get_votes_for_existing_activity_with_no_votes():
    """Test querying an activity that exists but has no votes yet."""
    admin_activities.append(
        Activity(
            id=101,
            name="No Votes Activity",
            description="Test",
            date="2024-03-15T14:00:00",
            location="Paris",
            type=ActivityType.sports,
            is_indoor=False
        )
    )
    
    response = client.get("/vote/activity/101")
    assert response.status_code == 200
    data = response.json()
    assert data["activity_id"] == 101
    assert data["total_votes"] == 0
    assert data["average_score"] == 0
    assert data["votes"] == []
