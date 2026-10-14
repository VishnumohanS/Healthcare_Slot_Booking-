from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_doctors_name_not_blank"),
        CheckConstraint("length(trim(specialization)) > 0", name="ck_doctors_specialization_not_blank"),
        CheckConstraint("start_hour >= 0 AND start_hour <= 23", name="ck_doctors_start_hour_range"),
        CheckConstraint("end_hour >= 1 AND end_hour <= 24", name="ck_doctors_end_hour_range"),
        CheckConstraint("end_hour > start_hour", name="ck_doctors_end_after_start"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    start_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    end_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_paise: Mapped[int] = mapped_column(Integer, nullable=False, default=50000, server_default="50000")
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
