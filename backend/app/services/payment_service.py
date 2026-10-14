import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from uuid import uuid4

import razorpay
from fastapi import HTTPException
from razorpay.errors import BadRequestError, GatewayError, ServerError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, NotFoundError
from app.models.appointment import STATUS_BOOKED, STATUS_CANCELLED, STATUS_PAYMENT_PENDING, Appointment
from app.models.doctor import Doctor
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentOrderRequest, PaymentVerifyRequest
from app.services.appointment_service import validate_slot
from app.services.doctor_service import get_doctor_or_404

logger = logging.getLogger(__name__)


def _razorpay_client():
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(
            status_code=503,
            detail="Razorpay is not configured. Add the test API key ID and secret to the backend .env file.",
        )
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_order(db: Session, patient: User, data: PaymentOrderRequest) -> dict:
    doctor = get_doctor_or_404(db, data.doctor_id)
    validate_slot(doctor, data.slot)

    now = datetime.utcnow()
    stale = list(db.scalars(select(Appointment).where(
        Appointment.doctor_id == doctor.id,
        Appointment.status == STATUS_PAYMENT_PENDING,
        Appointment.payment_expires_at <= now,
    )))
    for appointment in stale:
        appointment.status = STATUS_CANCELLED
    db.flush()

    occupied = db.scalars(select(Appointment).where(
        Appointment.doctor_id == doctor.id,
        Appointment.slot == data.slot,
        Appointment.status.in_([STATUS_BOOKED, "blocked", STATUS_PAYMENT_PENDING]),
    )).first()
    if occupied is not None:
        raise ConflictError("This doctor is already booked at that date and time.", code="slot_already_booked")

    try:
        order = _razorpay_client().order.create({
            "amount": doctor.fee_paise,
            "currency": "INR",
            "receipt": f"appt-{uuid4().hex[:32]}",
            "notes": {"doctor_id": str(doctor.id), "patient_id": str(patient.id)},
        })
    except (BadRequestError, GatewayError, ServerError) as exc:
        logger.exception("Razorpay could not create a payment order")
        raise HTTPException(status_code=502, detail="Razorpay could not start checkout. Please try again.") from exc
    order_id = order.get("id")
    if not isinstance(order_id, str) or not order_id:
        raise HTTPException(status_code=502, detail="Razorpay returned an invalid payment order.")
    appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        patient_name=patient.name,
        slot=data.slot,
        status=STATUS_PAYMENT_PENDING,
        payment_expires_at=now + timedelta(minutes=15),
    )
    db.add(appointment)
    try:
        db.flush()
        db.add(Payment(
            appointment_id=appointment.id,
            patient_id=patient.id,
            order_id=order_id,
            amount_paise=doctor.fee_paise,
        ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("This doctor is already booked at that date and time.", code="slot_already_booked") from exc
    db.refresh(appointment)
    return {
        "appointment_id": appointment.id,
        "order_id": order_id,
        "amount_paise": doctor.fee_paise,
        "currency": "INR",
        "key_id": settings.razorpay_key_id,
        "doctor_name": doctor.name,
        "patient_name": patient.name,
    }


def verify_payment(db: Session, patient: User, data: PaymentVerifyRequest) -> Appointment:
    payment = db.scalars(select(Payment).where(
        Payment.appointment_id == data.appointment_id,
        Payment.patient_id == patient.id,
        Payment.order_id == data.razorpay_order_id,
    )).first()
    if payment is None:
        raise NotFoundError("Payment order not found.", code="payment_not_found")

    appointment = db.get(Appointment, payment.appointment_id)
    if appointment is None:
        raise NotFoundError("Appointment not found.", code="appointment_not_found")
    if payment.status == "paid" and payment.payment_id == data.razorpay_payment_id:
        return appointment
    if appointment.status != STATUS_PAYMENT_PENDING:
        raise ConflictError("This payment order is no longer active.", code="payment_order_expired")
    if appointment.payment_expires_at is not None and appointment.payment_expires_at <= datetime.utcnow():
        appointment.status = STATUS_CANCELLED
        db.commit()
        raise ConflictError("The payment window expired. Please choose the slot again.", code="payment_order_expired")

    expected = hmac.new(
        settings.razorpay_key_secret.encode(),
        f"{data.razorpay_order_id}|{data.razorpay_payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, data.razorpay_signature):
        raise ConflictError("Razorpay payment signature is invalid.", code="invalid_payment_signature")

    appointment.status = STATUS_BOOKED
    appointment.payment_expires_at = None
    payment.status = "paid"
    payment.payment_id = data.razorpay_payment_id
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_order(db: Session, patient: User, appointment_id: int) -> None:
    payment = db.scalars(select(Payment).where(
        Payment.appointment_id == appointment_id,
        Payment.patient_id == patient.id,
        Payment.status == "pending",
    )).first()
    if payment is None:
        raise NotFoundError("Pending payment order not found.", code="payment_not_found")
    appointment = db.get(Appointment, appointment_id)
    if appointment is None or appointment.status != STATUS_PAYMENT_PENDING:
        raise ConflictError("This payment order is no longer active.", code="payment_order_expired")
    appointment.status = STATUS_CANCELLED
    payment.status = "cancelled"
    db.commit()
