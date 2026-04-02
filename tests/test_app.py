import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities_store)
    yield
    activities_store.clear()
    activities_store.update(copy.deepcopy(original))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]


def test_signup_duplicate():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_full():
    activity_name = "Chess Club"
    activities_store[activity_name]["participants"] = [f"student{i}@mergington.edu" for i in range(activities_store[activity_name]["max_participants"])]

    response = client.post(f"/activities/{activity_name}/signup", params={"email": "extra@mergington.edu"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_remove_participant_success():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_remove_participant_not_found():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "ghost@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
