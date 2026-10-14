"""Booking business rules (A-E). Routes stay thin; every rule lives here."""
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.models.appointment import (
    STATUS_BLOCKED,
    STATUS_BOOKED,
    STATUS_CANCELLED,
    STATUS_PAYMENT_PENDING,
    Appointment,
)
from app.models.doctor import Doctor
from app.models.user import User
from app.services import doctor_service


def validate_slot(doctor: Doctor, slot: datetime, duration_minutes: int | None = None) -> None:
    """Rule B: slot must be on a boundary and the whole appointment must fit in working hours."""
    duration = duration_minutes or settings.appointment_duration_minutes
    if slot <= datetime.now():
        raise UnprocessableError("Appointments must be scheduled in the future.", code="slot_in_past")
    start_minute = slot.hour * 60 + slot.minute

    if slot.second != 0 or slot.microsecond != 0 or start_minute % duration != 0:
        raise UnprocessableError(
            f"Appointments must start on a {duration}-minute boundary (e.g. 09:00, 09:{duration:02d}).",
            code="invalid_slot_boundary",
        )

    opens = doctor.start_hour * 60
    closes = doctor.end_hour * 60
    if start_minute < opens or start_minute + duration > closes:
        raise UnprocessableError(
            f"Dr. {doctor.name.removeprefix('Dr. ')} works {doctor.start_hour:02d}:00-{doctor.end_hour % 24:02d}:00; "
            f"a {duration}-minute appointment at {slot:%H:%M} does not fit inside those hours.",
            code="outside_working_hours",
        )


def _find_active_booking(db: Session, doctor_id: int, slot: datetime) -> Appointment | None:
    return db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.slot == slot,
            Appointment.status.in_([STATUS_BOOKED, STATUS_BLOCKED, STATUS_PAYMENT_PENDING]),
        )
    ).first()


def _slot_taken() -> ConflictError:
    return ConflictError("This doctor is already booked at that date and time.", code="slot_already_booked")


def block_slot(db: Session, doctor: Doctor, slot: datetime) -> Appointment:
    validate_slot(doctor, slot)
    if _find_active_booking(db, doctor.id, slot) is not None:
        raise _slot_taken()
    appointment = Appointment(doctor_id=doctor.id, slot=slot, status=STATUS_BLOCKED)
    db.add(appointment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if "unique" in str(exc.orig).lower():
            raise _slot_taken() from exc
        raise
    db.refresh(appointment)
    return appointment


def list_appointments(
    db: Session,
    user: User,
    doctor_id: int | None = None,
    on_date: date | None = None,
    include_cancelled: bool = False,
) -> list[Appointment]:
    query = select(Appointment)
    if user.role == "doctor":
        doctor = db.scalars(select(Doctor).where(Doctor.user_id == user.id)).first()
        if doctor is None:
            return []
        query = query.where(Appointment.doctor_id == doctor.id)
        if doctor_id is not None and doctor_id != doctor.id:
            return []
    else:
        query = query.where(Appointment.patient_id == user.id)
        if doctor_id is not None:
            query = query.where(Appointment.doctor_id == doctor_id)
    if on_date is not None:
        start = datetime.combine(on_date, time.min)
        query = query.where(Appointment.slot >= start, Appointment.slot < start + timedelta(days=1))
    if user.role == "doctor":
        query = query.where(Appointment.status != STATUS_PAYMENT_PENDING)
    if not include_cancelled:
        query = query.where(Appointment.status.in_([STATUS_BOOKED, STATUS_BLOCKED]))
    return list(db.scalars(query.order_by(Appointment.slot, Appointment.id)))


def get_appointment_or_404(db: Session, appointment_id: int, user: User) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None or (
        (user.role == "doctor" and appointment.status == STATUS_PAYMENT_PENDING)
        or
        (user.role == "patient" and appointment.patient_id != user.id)
        or (user.role == "doctor" and appointment.doctor_id != _doctor_id(db, user))
    ):
        raise NotFoundError(f"Appointment {appointment_id} not found.", code="appointment_not_found")
    return appointment


def _doctor_id(db: Session, user: User) -> int | None:
    doctor = db.scalars(select(Doctor).where(Doctor.user_id == user.id)).first()
    return doctor.id if doctor else None


def cancel_appointment(db: Session, appointment_id: int, user: User) -> Appointment:
    appointment = get_appointment_or_404(db, appointment_id, user)
    if appointment.status == STATUS_CANCELLED:
        raise ConflictError("Appointment is already cancelled.", code="already_cancelled")
    if user.role == "doctor":
        if appointment.status != STATUS_BLOCKED:
            raise ConflictError("Doctors can only remove their own blocked slots.", code="not_a_doctor_block")
    elif appointment.status == STATUS_BLOCKED:
        raise ConflictError("Doctor-blocked slots cannot be cancelled by patients.", code="not_patient_booking")
    elif appointment.slot <= datetime.now() + timedelta(hours=2):
        raise ConflictError(
            "Appointments can only be cancelled more than 2 hours before the scheduled time.",
            code="cancellation_window_closed",
        )
    appointment.status = STATUS_CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment


def available_slots(db: Session, doctor_id: int, on_date: date) -> list[str]:
    doctor = doctor_service.get_doctor_or_404(db, doctor_id)
    now = datetime.utcnow()
    stale = list(db.scalars(select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.status == STATUS_PAYMENT_PENDING,
        Appointment.payment_expires_at <= now,
    )))
    for appointment in stale:
        appointment.status = STATUS_CANCELLED
    if stale:
        db.commit()
    start = datetime.combine(on_date, time.min)
    return list(db.scalars(select(Appointment.slot).where(
        Appointment.doctor_id == doctor.id,
        Appointment.slot >= start,
        Appointment.slot < start + timedelta(days=1),
        Appointment.status.in_([STATUS_BOOKED, STATUS_BLOCKED, STATUS_PAYMENT_PENDING]),
    )))
