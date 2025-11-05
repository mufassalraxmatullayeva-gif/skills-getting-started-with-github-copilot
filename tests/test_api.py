from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep-ish copy of initial participants to restore after each test
    original = {k: v.copy() for k, v in activities.items()}
    # copy participants lists
    for v in original.values():
        v['participants'] = list(v.get('participants', []))

    yield

    # Restore
    activities.clear()
    for k, v in original.items():
        activities[k] = v


def test_get_activities():
    client = TestClient(app)
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Ensure a known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)

    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure not already in participants
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]

    # Signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # Signing up again should fail (400)
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 400

    # Unregister
    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregistering again should return 404
    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 404
