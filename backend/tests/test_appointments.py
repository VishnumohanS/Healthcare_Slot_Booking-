from datetime import datetime, timedelta
import hashlib
import hmac
import threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_patient_booking_requires_razorpay_verification(client, book, make_doctor):
    doctor = make_doctor()
    response = book(doctor["id"], "10:00:00")
    assert response.status_code == 200
    assert response.json()["status"] == "booked"
    assert response.json()["patient_name"] == "Jane Doe"


def test_duplicate_slot_is_rejected(client, book, make_doctor):
    doctor = make_doctor()
    assert book(doctor["id"]).status_code == 200
    response = client.post("/payments/orders", json={
        "doctor_id": doctor["id"], "slot": "2030-10-20T10:00:00",
    })
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "slot_already_booked"


def test_unverified_payment_does_not_confirm_booking(client, make_doctor):
    doctor = make_doctor()
    order = client.post("/payments/orders", json={
        "doctor_id": doctor["id"], "slot": "2030-10-20T10:00:00",
    }).json()
    response = client.post("/payments/verify", json={
        "appointment_id": order["appointment_id"],
        "razorpay_order_id": order["order_id"],
        "razorpay_payment_id": "pay_test_invalid",
        "razorpay_signature": "not-a-valid-signature",
    })
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_payment_signature"
    assert client.get("/appointments/").json() == []


def test_explicit_payment_signature_verifies_and_is_idempotent(client, make_doctor):
    doctor = make_doctor()
    order = client.post("/payments/orders", json={
        "doctor_id": doctor["id"], "slot": "2030-10-20T10:00:00",
    }).json()
    payment_id = "pay_test_" + uuid4().hex
    signature = hmac.new(
        settings.razorpay_key_secret.encode(),
        f"{order['order_id']}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    payload = {
        "appointment_id": order["appointment_id"],
        "razorpay_order_id": order["order_id"],
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    }
    first = client.post("/payments/verify", json=payload)
    second = client.post("/payments/verify", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["status"] == "booked"
    assert first.json()["id"] == second.json()["id"]


def test_cancelled_booking_releases_slot(client, book, make_doctor):
    doctor = make_doctor()
    appointment = book(doctor["id"]).json()
    cancelled = client.delete(f"/appointments/{appointment['id']}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert book(doctor["id"]).status_code == 200


def test_patient_can_cancel_only_more_than_two_hours_ahead(client, make_doctor, book):
    doctor = make_doctor(start_hour=0, end_hour=24)
    soon = datetime.now().replace(second=0, microsecond=0)
    soon += timedelta(minutes=30 - soon.minute % 30)
    if soon.date() == datetime.now().date() and soon.hour == 0:
        soon = soon.replace(hour=0)
    if soon.hour == 24:
        soon = soon + timedelta(days=1)
    result = book(doctor["id"], soon.strftime("%H:%M:%S"), day=soon.strftime("%Y-%m-%d"))
    assert result.status_code == 200, result.text
    response = client.delete(f"/appointments/{result.json()['id']}")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "cancellation_window_closed"


def test_patient_cannot_read_another_patients_appointment(client, make_doctor, book):
    doctor = make_doctor()
    appointment = book(doctor["id"]).json()
    another = client.post("/auth/register", json={
        "username": "another-patient", "password": "other-password",
        "name": "Other Patient", "role": "patient",
    }).json()
    response = client.get(f"/appointments/{appointment['id']}", headers={
        "Authorization": "Bearer " + another["access_token"],
    })
    assert response.status_code == 404
    assert client.get("/appointments/", headers={
        "Authorization": "Bearer " + another["access_token"],
    }).json() == []


def test_patient_cannot_block_doctor_slot(client, make_doctor):
    doctor = make_doctor()
    response = client.post("/appointments/block", json={"slot": "2030-10-20T10:00:00"})
    assert response.status_code == 403


def test_doctor_can_block_and_unblock_own_slot(client, make_doctor):
    doctor = make_doctor()
    headers = {"Authorization": "Bearer " + doctor["token"]}
    blocked = client.post("/appointments/block", headers=headers, json={"slot": "2030-10-20T10:00:00"})
    assert blocked.status_code == 201
    assert blocked.json()["status"] == "blocked"
    unavailable = client.get(f"/doctors/{doctor['id']}/availability?date=2030-10-20")
    assert unavailable.json()["occupied"] == ["2030-10-20T10:00:00"]
    removed = client.delete(f"/appointments/{blocked.json()['id']}", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["status"] == "cancelled"


def test_doctor_block_and_booking_cannot_overlap(client, make_doctor, book):
    doctor = make_doctor()
    headers = {"Authorization": "Bearer " + doctor["token"]}
    blocked = client.post("/appointments/block", headers=headers, json={"slot": "2030-10-20T10:00:00"})
    assert blocked.status_code == 201
    assert book(doctor["id"]).status_code == 409


def test_bad_slots_and_unknown_doctors_are_rejected(client, make_doctor):
    doctor = make_doctor()
    invalid_boundary = client.post("/payments/orders", json={
        "doctor_id": doctor["id"], "slot": "2030-10-20T10:15:00",
    })
    assert invalid_boundary.status_code == 422
    outside_hours = client.post("/payments/orders", json={
        "doctor_id": doctor["id"], "slot": "2030-10-20T17:00:00",
    })
    assert outside_hours.status_code == 422
    missing = client.post("/payments/orders", json={
        "doctor_id": 999, "slot": "2030-10-20T10:00:00",
    })
    assert missing.status_code == 404


def test_concurrent_payment_orders_reserve_exactly_one_slot(client, make_doctor):
    doctor = make_doctor()
    headers = {"Authorization": client.headers["Authorization"]}
    barrier = threading.Barrier(6)

    def attempt(_):
        with TestClient(app, raise_server_exceptions=False) as test_client:
            barrier.wait()
            return test_client.post(
                "/payments/orders",
                headers=headers,
                json={"doctor_id": doctor["id"], "slot": "2030-10-20T11:00:00"},
            ).status_code

    with ThreadPoolExecutor(max_workers=6) as pool:
        codes = list(pool.map(attempt, range(6)))
    assert codes.count(201) == 1
    assert codes.count(409) == 5


def test_openapi_exposes_auth_and_payment_routes(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/auth/register" in paths
    assert "/payments/orders" in paths
    assert "/doctors/me/reports" in paths
