from datetime import date

from fastapi import APIRouter, Path, Query

from app.dependencies import DoctorUser, DbSession
from app.schemas.common import ErrorResponse
from app.schemas.doctor import DoctorRead, DoctorUpdate
from app.services import doctor_service
from app.services import appointment_service

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=list[DoctorRead], summary="List all doctors")
def list_doctors(db: DbSession):
    return doctor_service.list_doctors(db)


@router.get("/me", response_model=DoctorRead)
def get_my_doctor_profile(db: DbSession, user: DoctorUser):
    return doctor_service.get_doctor_for_user(db, user)


@router.patch("/me", response_model=DoctorRead)
def update_my_doctor_profile(payload: DoctorUpdate, db: DbSession, user: DoctorUser):
    return doctor_service.update_doctor_profile(db, user, payload)


@router.get("/me/reports", summary="Doctor-only booking and revenue reports")
def get_my_reports(db: DbSession, user: DoctorUser):
    return doctor_service.doctor_report(db, doctor_service.get_doctor_for_user(db, user))


@router.get("/{doctor_id}/availability")
def get_availability(
    db: DbSession,
    doctor_id: int = Path(ge=1),
    on_date: date = Query(alias="date"),
):
    return {"occupied": appointment_service.available_slots(db, doctor_id, on_date)}


@router.get(
    "/{doctor_id}",
    response_model=DoctorRead,
    summary="Get a doctor by ID",
    responses={
        404: {"model": ErrorResponse, "description": "Doctor not found"},
        422: {"model": ErrorResponse, "description": "Invalid doctor ID"},
    },
)
def get_doctor(db: DbSession, doctor_id: int = Path(ge=1, description="Doctor ID")):
    return doctor_service.get_doctor_or_404(db, doctor_id)
