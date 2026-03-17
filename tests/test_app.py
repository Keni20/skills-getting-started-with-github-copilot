"""
Tests for Mergington High School Activities API

This test suite covers all FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for test isolation
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interscholastic play",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Tennis skills and friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["james@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and visual arts exploration",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["grace@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater performance and script writing",
        "schedule": "Mondays and Fridays, 3:45 PM - 5:15 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Competitive debate and public speaking skills",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:45 PM",
        "max_participants": 12,
        "participants": ["noah@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and scientific research",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset the activities dictionary to initial state before each test."""
    # Clear current activities
    activities.clear()
    # Restore initial data
    activities.update(INITIAL_ACTIVITIES.copy())
    yield
    # Cleanup after test (not strictly necessary since we reset at start)


class TestRootEndpoint:
    """Test the root endpoint that redirects to static files."""

    def test_root_redirect(self, client):
        # Arrange
        expected_content = "<!DOCTYPE html>"

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200  # TestClient follows redirects
        assert expected_content in response.text
        assert "Mergington High School" in response.text


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_all_activities(self, client, reset_activities):
        # Arrange
        expected_activity_count = len(INITIAL_ACTIVITIES)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_structure(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        activity = data[activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_participants_count(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        expected_count = len(INITIAL_ACTIVITIES[activity_name]["participants"])

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data[activity_name]["participants"]) == expected_count


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_signup_invalid_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_missing_email(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_valid(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"  # Not signed up
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_unregister_invalid_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_missing_email(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data