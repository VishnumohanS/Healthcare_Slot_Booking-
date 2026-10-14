def test_registration_and_login_return_role_scoped_sessions(client):
    registered = client.post("/auth/register", json={
        "username": "new-patient",
        "password": "a-secure-password",
        "name": "New Patient",
        "role": "patient",
    })
    assert registered.status_code == 201
    assert registered.json()["user"]["role"] == "patient"

    signed_in = client.post("/auth/login", json={
        "username": "NEW-PATIENT",
        "password": "a-secure-password",
    })
    assert signed_in.status_code == 200
    assert signed_in.json()["user"]["username"] == "new-patient"


def test_duplicate_username_and_invalid_credentials_are_rejected(client):
    duplicate = client.post("/auth/register", json={
        "username": "TEST-PATIENT",
        "password": "another-password",
        "name": "Duplicate",
        "role": "patient",
    })
    assert duplicate.status_code == 409
    invalid = client.post("/auth/login", json={
        "username": "test-patient",
        "password": "wrong-password",
    })
    assert invalid.status_code == 401


def test_protected_routes_require_a_valid_session(client):
    response = client.get("/appointments/", headers={"Authorization": ""})
    assert response.status_code == 401
    response = client.get("/doctors/me/reports", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_patient_account_cannot_create_doctor_profile(client):
    response = client.patch("/doctors/me", json={
        "name": "Not a doctor",
        "specialization": "General",
        "start_hour": 9,
        "end_hour": 17,
        "fee_paise": 50000,
        "bio": "",
    })
    assert response.status_code == 403


def test_bearer_authentication_is_allowed_by_cors(client):
    response = client.options(
        "/appointments/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
