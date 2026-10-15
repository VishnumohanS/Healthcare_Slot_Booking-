import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_LOCAL_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$")


def _parse_local_datetime(value):
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            raise ValueError("slot must not include a timezone offset")
        return value
    if not isinstance(value, str) or not _LOCAL_ISO.match(value.strip()):
        raise ValueError(
            "slot must be an ISO-8601 local datetime such as 2030-10-20T10:00:00 (no timezone offset)"
        )
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError("slot is not a valid calendar date/time") from exc


class AppointmentCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{"doctor_id": 1, "patient_name": "Jane Doe", "slot": "2030-10-20T10:00:00"}]
        },
    )

    doctor_id: int = Field(strict=True, ge=1)
    patient_name: str = Field(min_length=1, max_length=100)
    slot: datetime = Field(
        description=(
            "Appointment start as a clinic-local ISO-8601 datetime WITHOUT a timezone offset, "
            "e.g. 2030-10-20T10:00:00. Must fall on a slot boundary inside the doctor's working hours."
        )
    )

    @field_validator("slot", mode="before")
    @classmethod
    def _strict_local_datetime(cls, value):
        return _parse_local_datetime(value)


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    patient_id: int | None = None
    patient_name: str | None
    slot: datetime
    status: Literal["booked", "cancelled", "blocked", "payment_pending"]


class AppointmentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot: datetime

    @field_validator("slot", mode="before")
    @classmethod
    def _strict_local_datetime(cls, value):
        return _parse_local_datetime(value)
