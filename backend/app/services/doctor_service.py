from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, NotFoundError
from app.models.appointment import Appointment, STATUS_BLOCKED, STATUS_BOOKED, STATUS_PAYMENT_PENDING
from app.models.doctor import Doctor
from app.models.payment import Payment
from app.models.user import User
from app.schemas.doctor import DoctorUpdate


def get_doctor_for_user(db: Session, user: User) -> Doctor:
    doctor = db.scalars(select(Doctor).where(Doctor.user_id == user.id)).first()
    if doctor is None:
        raise NotFoundError("Doctor profile not found.", code="doctor_profile_not_found")
    return doctor


def update_doctor_profile(db: Session, user: User, data: DoctorUpdate) -> Doctor:
    doctor = get_doctor_for_user(db, user)
    if (doctor.start_hour, doctor.end_hour) != (data.start_hour, data.end_hour):
        active = db.scalars(select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_([STATUS_BOOKED, STATUS_BLOCKED, STATUS_PAYMENT_PENDING]),
        ))
        opens = data.start_hour * 60
        closes = data.end_hour * 60
        if any(
            appointment.slot.hour * 60 + appointment.slot.minute < opens
            or appointment.slot.hour * 60 + appointment.slot.minute + settings.appointment_duration_minutes > closes
            for appointment in active
        ):
            raise ConflictError(
                "Working hours cannot exclude an already reserved appointment or blocked slot.",
                code="hours_conflict_with_schedule",
            )
    for key, value in data.model_dump().items():
        setattr(doctor, key, value)
    user.name = data.name
    db.commit()
    db.refresh(doctor)
    return doctor


def doctor_report(db: Session, doctor: Doctor) -> dict:
    appointments = list(db.scalars(select(Appointment).where(Appointment.doctor_id == doctor.id)))
    active = sum(appointment.status == "booked" for appointment in appointments)
    cancelled = sum(appointment.status == "cancelled" for appointment in appointments)
    blocked = sum(appointment.status == "blocked" for appointment in appointments)
    revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount_paise), 0))
        .join(Appointment, Payment.appointment_id == Appointment.id)
        .where(Appointment.doctor_id == doctor.id, Payment.status == "paid")
    )

    today = date.today().replace(day=1)
    months = []
    for offset in range(5, -1, -1):
        month_number = today.month - offset
        year = today.year + (month_number - 1) // 12
        month_number = (month_number - 1) % 12 + 1
        start = datetime(year, month_number, 1)
        next_year = year + (1 if month_number == 12 else 0)
        next_month_number = 1 if month_number == 12 else month_number + 1
        next_month = datetime(next_year, next_month_number, 1)
        months.append({
            "month": start.strftime("%b %Y"),
            "appointments": sum(
                item.status == "booked" and start <= item.slot < next_month for item in appointments
            ),
        })
    return {
        "total_appointments": active,
        "cancelled_appointments": cancelled,
        "blocked_slots": blocked,
        "revenue_paise": revenue,
        "monthly_bookings": months,
    }


def list_doctors(db: Session) -> list[Doctor]:
    return list(db.scalars(select(Doctor).order_by(Doctor.id)))


def get_doctor_or_404(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise NotFoundError(f"Doctor {doctor_id} not found.", code="doctor_not_found")
    return doctor
