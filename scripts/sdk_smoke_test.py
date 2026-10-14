"""Smoke test for the GENERATED Python SDK (health_sdk). Requires the backend to be running.

    python scripts/sdk_smoke_test.py [http://127.0.0.1:8000]

Method names/signatures below are taken from the generated code (e.g. the `date` query
parameter is generated as `var_date`).
"""
import sys
import uuid
from datetime import date

from health_sdk import ApiClient, Configuration
from health_sdk.api.appointments_api import AppointmentsApi
from health_sdk.api.doctors_api import DoctorsApi
from health_sdk.exceptions import ApiException
from health_sdk.models.appointment_create import AppointmentCreate
from health_sdk.models.doctor_create import DoctorCreate
from datetime import datetime

host = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
configuration = Configuration(host=host)

with ApiClient(configuration) as client:
    doctors_api, appts_api = DoctorsApi(client), AppointmentsApi(client)

    before = doctors_api.list_doctors()
    print(f"list_doctors -> {len(before)} doctor(s)")

    doctor = doctors_api.create_doctor(
        DoctorCreate(name=f"SDK Doctor {uuid.uuid4().hex[:6]}", specialization="Testing", start_hour=9, end_hour=17)
    )
    print("create_doctor ->", doctor.id, doctor.name)
    assert doctors_api.get_doctor(doctor.id).id == doctor.id
    assert len(doctors_api.list_doctors()) == len(before) + 1

    slot = datetime(2031, 3, 4, 10, 0, 0)
    appt = appts_api.book_appointment(AppointmentCreate(doctor_id=doctor.id, patient_name="SDK Patient", slot=slot))
    print("book_appointment ->", appt.id, appt.slot, appt.status)

    try:
        appts_api.book_appointment(AppointmentCreate(doctor_id=doctor.id, patient_name="Dup", slot=slot))
        raise SystemExit("FAIL: duplicate booking was accepted")
    except ApiException as exc:
        assert exc.status == 409, exc.status
        print("duplicate booking correctly rejected with HTTP", exc.status)

    listed = appts_api.list_appointments(doctor_id=doctor.id, var_date=date(2031, 3, 4))
    assert [a.id for a in listed] == [appt.id]
    cancelled = appts_api.cancel_appointment(appt.id)
    assert cancelled.status == "cancelled"
    print("cancel_appointment ->", cancelled.status)
    assert appts_api.book_appointment(AppointmentCreate(doctor_id=doctor.id, patient_name="Again", slot=slot)).status == "booked"

print("SDK smoke test PASSED")
