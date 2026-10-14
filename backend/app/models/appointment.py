from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

STATUS_BOOKED = "booked"
STATUS_CANCELLED = "cancelled"
STATUS_BLOCKED = "blocked"
STATUS_PAYMENT_PENDING = "payment_pending"

# Canonical, microsecond-free text storage ("YYYY-MM-DD HH:MM:SS"). Using one fixed format means the
# unique index compares identical strings whether a row came from the API or from seed_data.sql.
SlotType = DateTime().with_variant(
    sqlite.DATETIME(
        storage_format="%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d"
    ),
    "sqlite",
)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('booked', 'cancelled', 'blocked', 'payment_pending')",
            name="ck_appointments_status",
        ),
        CheckConstraint(
            "patient_name IS NULL OR length(trim(patient_name)) > 0",
            name="ck_appointments_patient_not_blank",
        ),
        # Active bookings, doctor blocks, and pending checkouts reserve their slot.
        Index(
            "uq_appointments_active_doctor_slot",
            "doctor_id",
            "slot",
            unique=True,
            sqlite_where=text("status IN ('booked', 'blocked', 'payment_pending')"),
        ),
        Index("ix_appointments_slot", "slot"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    patient_name: Mapped[str | None] = mapped_column(String(100))
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    slot: Mapped[datetime] = mapped_column(SlotType, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=STATUS_BOOKED, server_default=STATUS_BOOKED
    )
    payment_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
