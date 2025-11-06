"""
Test UC5: Administrator enriching activity listings
Test UC6: Configuration management
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_admin_add_custom_activity():
    """UC5: Admin can add custom activities to enrich listings."""
    activity_data = {
        "id": 99999,
        "name": "Local Farmers Market",
        "type": "community",
        "location": "Paris",
        "is_indoor": False,
        "date": "2025-11-10",
        "description": "Weekly farmers market with local produce and crafts",
    }

    response = client.post("/admin/activity", json=activity_data)
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "Local Farmers Market"
    assert result["location"] == "Paris"
    print("UC5: Admin can add custom activity")


def test_admin_list_activities_requires_admin():
    """UC5: Admin activities endpoint requires administrator role."""
    response = client.get(
        "/admin/activities",
        params={
            "city": "Paris",
            "countryCode": "FR",
            "date": "2025-11-10",
            "admin_user_id": 99999,
        },
    )
    assert response.status_code == 403
    assert "Administrator privileges required" in response.json()["detail"]
    print("UC5: Admin endpoint rejects non-admin users")


def test_admin_list_activities_with_admin_user():
    """UC5: Admin can list combined Ticketmaster + custom activities."""
    response = client.get(
        "/admin/activities",
        params={
            "city": "Paris",
            "countryCode": "FR",
            "date": "2025-11-10",
            "admin_user_id": 3,
        },
    )
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, list)
    print(f" UC5: Admin retrieved {len(activities)} activities (Ticketmaster + custom)")


def test_admin_view_configuration():
    """UC6: Admin can view application configuration."""
    response = client.get("/admin/config", params={"admin_user_id": 3})
    assert response.status_code == 200
    config = response.json()

    assert "app" in config
    assert "data_sources" in config
    assert "recommendations" in config
    assert "activities" in config

    assert "weather" in config["data_sources"]
    assert "air_quality" in config["data_sources"]
    assert "events" in config["data_sources"]

    assert "outdoor_conditions" in config["recommendations"]
    assert "indoor_conditions" in config["recommendations"]
    assert "confidence_threshold" in config["recommendations"]

    print("UC6: Admin can view configuration")
    print(f"  - Weather provider: {config['data_sources']['weather']['provider']}")
    print(
        f"  - Confidence threshold: {config['recommendations']['confidence_threshold']}"
    )


def test_config_view_requires_admin():
    """UC6: Configuration endpoint requires administrator role."""
    response = client.get("/admin/config", params={"admin_user_id": 1})
    assert response.status_code == 403
    print("UC6: Config endpoint rejects non-admin users")


if __name__ == "__main__":
    print("\n=== Testing UC5: Admin Activity Enrichment ===")
    test_admin_add_custom_activity()
    test_admin_list_activities_requires_admin()
    test_admin_list_activities_with_admin_user()

    print("\n=== Testing UC6: Configuration Management ===")
    test_admin_view_configuration()
    test_config_view_requires_admin()

    print("\nAll UC5 and UC6 tests passed!")
