from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_succeeds():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "duplicate@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    first_response = client.post(url, params={"email": email})
    duplicate_response = client.post(url, params={"email": email})
    payload = duplicate_response.json()

    # Assert
    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert payload["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = quote("Nonexistent Activity", safe="")
    email = "someone@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"
