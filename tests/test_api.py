from src.app import activities


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_names = set(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json()) == expected_names


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity = "Does Not Exist"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    participants_before = list(activities[activity]["participants"])

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert activities[activity]["participants"] == participants_before


def test_signup_full_activity_returns_400(client):
    # Arrange
    activity = "Chess Club"
    details = activities[activity]
    while len(details["participants"]) < details["max_participants"]:
        details["participants"].append(f"student{len(details['participants'])}@mergington.edu")
    email = "late.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert email not in details["participants"]


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_student_not_signed_up_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "not.signed.up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity = "Does Not Exist"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_signup_then_unregister_restores_state(client):
    # Arrange
    activity = "Drama Club"
    email = "round.trip@mergington.edu"
    participants_before = list(activities[activity]["participants"])
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert activities[activity]["participants"] == participants_before
