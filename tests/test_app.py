"""
pytest suite for High School Management System API endpoints.

This module contains comprehensive tests for all FastAPI endpoints using
the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Copy of initial activities for test isolation
initial_activities = {
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
        "description": "Competitive basketball training and games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Swimming Club": {
        "description": "Swimming training and water sports",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Art Studio": {
        "description": "Express creativity through painting and drawing",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Drama Club": {
        "description": "Theater arts and performance training",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Team": {
        "description": "Learn public speaking and argumentation skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Hands-on experiments and scientific exploration",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    }
}


@pytest.fixture
def client():
    """
    Create a TestClient for the FastAPI app and reset activities before each test.
    
    This fixture ensures test isolation by resetting the global activities
    dictionary to its initial state before each test.
    """
    # Arrange: Reset activities to initial state (deep copy to avoid shared lists)
    activities.clear()
    activities.update(deepcopy(initial_activities))
    
    # Act: Create and return the test client
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html."""
        # Arrange: Request is prepared with follow_redirects=False to capture redirect
        
        # Act: Send GET request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Should redirect with 307 status code
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client):
        """Test that GET /activities returns all activities as a dictionary."""
        # Arrange: Client is prepared
        
        # Act: Send GET request to /activities
        response = client.get("/activities")
        
        # Assert: Response should contain all activities
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data

    def test_get_activities_includes_all_fields(self, client):
        """Test that each activity includes all required fields."""
        # Arrange: Client is prepared
        
        # Act: Send GET request to /activities
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: Each activity should have required fields
        for activity_name, activity in activities_data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_preserves_participants(self, client):
        """Test that participant lists are preserved in the response."""
        # Arrange: Client is prepared
        
        # Act: Send GET request to /activities
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: Chess Club should have initial participants
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """Test successful signup for a new participant."""
        # Arrange: Prepare signup request for an available activity
        activity_name = "Basketball Team"
        email = "new_student@mergington.edu"
        
        # Act: Send POST request to signup endpoint
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 200 with success message
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_participant_actually_added(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Arrange: Prepare signup for an activity
        activity_name = "Basketball Team"
        email = "participant@mergington.edu"
        
        # Act: Send POST request to signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Verify by retrieving activities
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: New participant should be in the list
        assert email in activities_data[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404."""
        # Arrange: Prepare request for activity that doesn't exist
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Send POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that duplicate signup returns 400 error."""
        # Arrange: Participant is already enrolled
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Send POST request to signup for same activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Should return 400 error for duplicate
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can signup for multiple different activities."""
        # Arrange: Prepare signups for different activities
        email = "versatile_student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Drama Club"]
        
        # Act: Sign up for multiple activities
        for activity_name in activities_to_join:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Verify enrollments
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: Student should be in all activities
        for activity_name in activities_to_join:
            assert email in activities_data[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the POST /activities/{activity_name}/remove endpoint."""

    def test_remove_existing_participant_success(self, client):
        """Test successful removal of an existing participant."""
        # Arrange: Participant is already enrolled
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Send POST request to remove endpoint
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert: Should return 200 with success message
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_actually_removed(self, client):
        """Test that remove actually removes the participant."""
        # Arrange: Participant is enrolled
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Send POST request to remove
        client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        # Verify by retrieving activities
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: Participant should no longer be in the list
        assert email not in activities_data[activity_name]["participants"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that removing from nonexistent activity returns 404."""
        # Arrange: Prepare request for activity that doesn't exist
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Send POST request to remove
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert: Should return 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonenrolled_participant_returns_400(self, client):
        """Test that removing unenrolled participant returns 400."""
        # Arrange: Participant is not enrolled
        activity_name = "Basketball Team"  # No participants initially
        email = "not_enrolled@mergington.edu"
        
        # Act: Send POST request to remove
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert: Should return 400 error
        assert response.status_code == 400
        assert "not enrolled" in response.json()["detail"]

    def test_remove_and_rejoin_activity(self, client):
        """Test that participant can be removed and then re-joined."""
        # Arrange: Participant is initially enrolled
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Remove participant
        client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        # Re-enroll the participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Second signup should succeed and participant should be re-enrolled
        assert response.status_code == 200
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints."""

    def test_signup_remove_signup_workflow(self, client):
        """Test a complete workflow of signup, remove, and re-signup."""
        # Arrange: Set up test data
        activity_name = "Art Studio"
        email = "artist@mergington.edu"
        
        # Act & Assert: Signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Act & Assert: Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Act & Assert: Remove
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Act & Assert: Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # Act & Assert: Re-signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Act & Assert: Final verification
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]

    def test_multiple_students_concurrent_signups(self, client):
        """Test that multiple students can signup for the same activity."""
        # Arrange: Prepare multiple student emails
        activity_name = "Programming Class"
        new_students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act: All students signup
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: All students are now enrolled
        response = client.get("/activities")
        activities_data = response.json()
        for email in new_students:
            assert email in activities_data[activity_name]["participants"]
        
        # Total participants should include original + new
        total_participants = len(activities_data[activity_name]["participants"])
        assert total_participants == 5  # 2 original + 3 new

    def test_activity_capacity_tracking(self, client):
        """Test that activity capacity information is accessible."""
        # Arrange: Request activities data
        
        # Act: Get all activities
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert: Each activity should have max capacity and current participants
        for activity_name, activity in activities_data.items():
            assert activity["max_participants"] > 0
            assert len(activity["participants"]) <= activity["max_participants"]
