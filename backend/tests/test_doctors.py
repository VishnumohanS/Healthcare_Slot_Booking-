def test_registered_doctor_gets_public_profile(client, make_doctor):
    doctor = make_doctor(name="Dr. Test", specialization="General")
    response = client.get("/doctors/")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Dr. Test"
    assert response.json()[0]["fee_paise"] == 50000


def test_doctor_can_update_only_own_profile(client, make_doctor):
    first = make_doctor(name="Dr. One")
    second = make_doctor(name="Dr. Two")
    headers = {"Authorization": "Bearer " + first["token"]}
    updated = client.patch("/doctors/me", headers=headers, json={
        "name": "Dr. One Updated",
        "specialization": "Cardiology",
        "start_hour": 8,
        "end_hour": 16,
        "fee_paise": 75000,
        "bio": "Cardiology specialist",
    })
    assert updated.status_code == 200
    assert updated.json()["name"] == "Dr. One Updated"
    assert updated.json()["fee_paise"] == 75000
    assert client.get(f"/doctors/{second['id']}").json()["name"] == "Dr. Two"


def test_patient_cannot_read_doctor_profile_or_reports(client):
    assert client.get("/doctors/me").status_code == 403
    assert client.get("/doctors/me/reports").status_code == 403


def test_doctor_reports_only_own_appointments(client, make_doctor, book):
    first = make_doctor(name="Dr. One")
    second = make_doctor(name="Dr. Two")
    book(first["id"])
    book(second["id"])
    reports = client.get("/doctors/me/reports", headers={
        "Authorization": "Bearer " + first["token"],
    })
    assert reports.status_code == 200
    assert reports.json()["total_appointments"] == 1
    assert reports.json()["revenue_paise"] == 50000
    assert len(reports.json()["monthly_bookings"]) == 6
    schedule = client.get("/appointments/", headers={"Authorization": "Bearer " + first["token"]})
    assert all(item["doctor_id"] == first["id"] for item in schedule.json())


def test_registration_requires_valid_doctor_profile_fields(client):
    response = client.post("/auth/register", json={
        "username": "invalid-doctor",
        "password": "secret-password",
        "name": "Dr. Invalid",
        "role": "doctor",
        "specialization": "General",
        "start_hour": 17,
        "end_hour": 9,
        "fee_paise": 0,
    })
    assert response.status_code == 422


def test_working_hours_cannot_exclude_existing_bookings(client, make_doctor, book):
    doctor = make_doctor()
    book(doctor["id"], "16:30:00")
    updated = client.patch("/doctors/me", headers={
        "Authorization": "Bearer " + doctor["token"],
    }, json={
        "name": doctor["name"],
        "specialization": doctor["specialization"],
        "start_hour": 9,
        "end_hour": 16,
        "fee_paise": doctor["fee_paise"],
        "bio": "",
    })
    assert updated.status_code == 409
    assert updated.json()["error"]["code"] == "hours_conflict_with_schedule"
