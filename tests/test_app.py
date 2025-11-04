from fastapi.testclient import TestClient
import uuid

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check: one of the seeded activities exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    # create a unique email to avoid collisions
    email = f"testuser+{uuid.uuid4().hex}@example.com"

    # ensure email not already present
    assert email not in activities[activity]["participants"]

    # sign up
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    # message may have URL-decoded characters; just check it acknowledged the signup
    msg = signup_resp.json().get("message", "")
    assert "Signed up" in msg and activity in msg

    # verify added
    assert any(p.strip().lower() == email.strip().lower() for p in activities[activity]["participants"])

    # double-signup should fail
    dup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup_resp.status_code == 400

    # unregister
    del_resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert del_resp.status_code == 200
    assert f"Unregistered" in del_resp.json().get("message", "")

    # verify removed
    assert not any(p.strip().lower() == email.strip().lower() for p in activities[activity]["participants"])

    # unregistering again should return 404
    del_again = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert del_again.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/NoSuchActivity/unregister?email=foo@example.com")
    assert resp.status_code == 404
    