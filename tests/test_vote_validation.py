"""
Tests for vote validation - ensuring votes only accepted for existing activities.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.admin import admin_activities
from app.models.db.activity import Activity, ActivityType
from app.services import vote_service


@pytest.fixture(autouse=True)
def reset_votes():
    """Clear votes before each test."""
    vote_service._VOTES.clear()
    yield
    vote_service._VOTES.clear()


@pytest.fixture(autouse=True)
def setup_admin_activities():
    """Ensure we have at least one admin activity for testing."""
    admin_activities.clear()
    admin_activities.append(
        Activity(
            id=999,
            name="Test Admin Activity",
            description="For testing purposes",
            date="2024-03-15T14:00:00",
            location="Test City",
            type=ActivityType.cultural,
            is_indoor=False
        )
    )
    yield
    admin_activities.clear()


client = TestClient(app)


def test_vote_for_nonexistent_activity():
    """Test that voting for a non-existent activity returns 404."""
    vote_payload = {
        "votes": [
            {"user_id": 1, "activity_id": 99999, "score": 8}
        ]
    }
    
    response = client.post("/vote/", json=vote_payload)
    assert response.status_code == 404
    assert "Activity with id 99999 does not exist" in response.json()["detail"]


def test_vote_for_existing_admin_activity():
    """Test that voting for an existing admin activity succeeds."""
    vote_payload = {
        "votes": [
            {"user_id": 1, "activity_id": 999, "score": 9}
        ]
    }
    
    response = client.post("/vote/", json=vote_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "ok"
    assert response.json()["votes_recorded"] == 1


def test_vote_mixed_existing_and_nonexistent():
    """Test that voting with a mix of existing and non-existing activities fails."""
    vote_payload = {
        "votes": [
            {"user_id": 1, "activity_id": 999, "score": 9},  # exists
            {"user_id": 1, "activity_id": 88888, "score": 7}  # doesn't exist
        ]
    }
    
    response = client.post("/vote/", json=vote_payload)
    assert response.status_code == 404
    assert "Activity with id 88888 does not exist" in response.json()["detail"]
    
    # Verify no votes were recorded (transaction-like behavior)
    all_votes = vote_service.list_votes()
    assert len(all_votes) == 0


def test_vote_multiple_existing_activities():
    """Test voting for multiple existing admin activities."""
    # Add another admin activity
    admin_activities.append(
        Activity(
            id=998,
            name="Second Test Activity",
            description="Another test",
            date="2024-03-16T14:00:00",
            location="Test City",
            type=ActivityType.sports,
            is_indoor=True
        )
    )
    
    vote_payload = {
        "votes": [
            {"user_id": 1, "activity_id": 999, "score": 9},
            {"user_id": 1, "activity_id": 998, "score": 8}
        ]
    }
    
    response = client.post("/vote/", json=vote_payload)
    assert response.status_code == 201
    assert response.json()["votes_recorded"] == 2
    
    # Verify both votes were recorded
    all_votes = vote_service.list_votes()
    assert len(all_votes) == 2
