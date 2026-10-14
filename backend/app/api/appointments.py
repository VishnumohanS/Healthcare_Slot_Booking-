from datetime import date

from fastapi import APIRouter, Path, Query

from app.dependencies import CurrentUser, DbSession, DoctorUser
from app.schemas.appointment import AppointmentBlock, AppointmentRead
from app.schemas.common import ErrorResponse
from app.services import appointment_service
from app.services.doctor_service import get_doctor_for_user

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/block", response_model=AppointmentRead, status_code=201, summary="Block one of your slots")
def block_slot(payload: AppointmentBlock, db: DbSession, user: DoctorUser):
    doctor = get_doctor_for_user(db, user)
    return appointment_service.block_slot(db, doctor, payload.slot)


@router.get(
    "/",
    response_model=list[AppointmentRead],
    summary="List appointments",
    description="Active appointments ordered by time. Filter by doctor and/or calendar date (`YYYY-MM-DD`).",
    responses={422: {"model": ErrorResponse, "description": "Invalid filter value"}},
)
def list_appointments(
    db: DbSession,
    user: CurrentUser,
    doctor_id: int | None = Query(default=None, ge=1, description="Only this doctor's appointments"),
    date: date | None = Query(default=None, description="Only appointments on this date (YYYY-MM-DD)"),
    include_cancelled: bool = Query(default=False, description="Also return cancelled appointments"),
):
    return appointment_service.list_appointments(db, user, doctor_id, date, include_cancelled)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentRead,
    summary="Get an appointment by ID",
    responses={
        404: {"model": ErrorResponse, "description": "Appointment not found"},
        422: {"model": ErrorResponse, "description": "Invalid appointment ID"},
    },
)
def get_appointment(db: DbSession, user: CurrentUser, appointment_id: int = Path(ge=1)):
    return appointment_service.get_appointment_or_404(db, appointment_id, user)


@router.delete(
    "/{appointment_id}",
    response_model=AppointmentRead,
    summary="Cancel an appointment",
    description="Marks the appointment `cancelled` and frees the slot. Returns the cancelled appointment.",
    responses={
        404: {"model": ErrorResponse, "description": "Appointment not found"},
        409: {"model": ErrorResponse, "description": "Appointment already cancelled"},
        422: {"model": ErrorResponse, "description": "Invalid appointment ID"},
    },
)
def cancel_appointment(db: DbSession, user: CurrentUser, appointment_id: int = Path(ge=1)):
    return appointment_service.cancel_appointment(db, appointment_id, user)
