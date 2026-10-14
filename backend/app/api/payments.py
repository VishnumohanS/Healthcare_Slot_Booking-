from fastapi import APIRouter, status

from app.dependencies import DbSession, PatientUser
from app.schemas.appointment import AppointmentRead
from app.schemas.payment import PaymentOrderRead, PaymentOrderRequest, PaymentVerifyRequest
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/orders", response_model=PaymentOrderRead, status_code=status.HTTP_201_CREATED)
def create_payment_order(payload: PaymentOrderRequest, db: DbSession, user: PatientUser):
    return payment_service.create_order(db, user, payload)


@router.post("/verify", response_model=AppointmentRead)
def verify_payment(payload: PaymentVerifyRequest, db: DbSession, user: PatientUser):
    return payment_service.verify_payment(db, user, payload)


@router.post("/{appointment_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_payment_order(appointment_id: int, db: DbSession, user: PatientUser):
    payment_service.cancel_order(db, user, appointment_id)
