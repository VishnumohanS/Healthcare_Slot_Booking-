from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.appointment import _parse_local_datetime


class PaymentOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doctor_id: int = Field(strict=True, ge=1)
    slot: datetime

    @field_validator("slot", mode="before")
    @classmethod
    def _strict_local_datetime(cls, value):
        return _parse_local_datetime(value)


class PaymentOrderRead(BaseModel):
    appointment_id: int
    order_id: str
    amount_paise: int
    currency: str = "INR"
    key_id: str
    doctor_name: str
    patient_name: str


class PaymentVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    appointment_id: int = Field(strict=True, ge=1)
    razorpay_order_id: str = Field(min_length=1, max_length=100)
    razorpay_payment_id: str = Field(min_length=1, max_length=100)
    razorpay_signature: str = Field(min_length=1, max_length=256)
