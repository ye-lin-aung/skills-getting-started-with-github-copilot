import pytest
from fastapi.testclient import TestClient


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that GET /activities returns expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Basketball" in activities
        assert "Tennis" in activities
        assert "Programming Class" in activities

    def test_get_activities_activity_structure(self, client, reset_activities):
        """Test that each activity has the expected structure"""
        response = client.get("/activities")
        activities = response.json()
        
        basketball = activities["Basketball"]
        
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)

    def test_get_activities_initial_participants(self, client, reset_activities):
        """Test that initial participants are present"""
        response = client.get("/activities")
        activities = response.json()
        
        basketball = activities["Basketball"]
        assert "alex@mergington.edu" in basketball["participants"]
        assert "jordan@mergington.edu" in basketball["participants"]


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Tennis/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "newstudent@mergington.edu" in activities["Tennis"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """Test that signing up with an already registered email returns 400"""
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_multiple_signups_to_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        response2 = client.post(f"/activities/Tennis/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Basketball"]["participants"]
        assert email in activities["Tennis"]["participants"]

    def test_signup_with_empty_email_parameter(self, client, reset_activities):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Basketball/signup?email=")
        
        # This should technically succeed and add an empty string, but let's verify current behavior
        assert response.status_code == 200

    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup correctly updates the participant count"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Drama Club"]["participants"])
        
        client.post("/activities/Drama Club/signup?email=newcomer@mergington.edu")
        
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Drama Club"]["participants"])
        
        assert updated_count == initial_count + 1


class TestRootEndpoint:
    """Test the GET / endpoint"""

    def test_root_redirects_to_static(self, client, reset_activities):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivityDataIntegrity:
    """Test data integrity and consistency"""

    def test_activities_have_consistent_structure(self, client, reset_activities):
        """Test that all activities have the same keys"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == expected_keys

    def test_max_participants_is_positive_integer(self, client, reset_activities):
        """Test that max_participants is a positive integer"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_participants_are_strings(self, client, reset_activities):
        """Test that all participants in lists are strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
