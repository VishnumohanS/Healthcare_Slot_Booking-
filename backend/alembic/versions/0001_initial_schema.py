"""Initial schema: doctors and appointments

Revision ID: 0001
Revises:
Create Date: 2026-10-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("specialization", sa.String(100), nullable=False),
        sa.Column("start_hour", sa.Integer(), nullable=False),
        sa.Column("end_hour", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_doctors_name_not_blank"),
        sa.CheckConstraint("length(trim(specialization)) > 0", name="ck_doctors_specialization_not_blank"),
        sa.CheckConstraint("start_hour >= 0 AND start_hour <= 23", name="ck_doctors_start_hour_range"),
        sa.CheckConstraint("end_hour >= 1 AND end_hour <= 24", name="ck_doctors_end_hour_range"),
        sa.CheckConstraint("end_hour > start_hour", name="ck_doctors_end_after_start"),
    )
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("patient_name", sa.String(100), nullable=False),
        sa.Column("slot", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="booked"),
        sa.CheckConstraint("status IN ('booked', 'cancelled')", name="ck_appointments_status"),
        sa.CheckConstraint("length(trim(patient_name)) > 0", name="ck_appointments_patient_not_blank"),
    )
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_slot", "appointments", ["slot"])
    # Partial unique index: only ACTIVE bookings are unique per doctor+slot (cancelled rows are ignored).
    op.create_index(
        "uq_appointments_active_doctor_slot",
        "appointments",
        ["doctor_id", "slot"],
        unique=True,
        sqlite_where=sa.text("status = 'booked'"),
    )


def downgrade() -> None:
    op.drop_index("uq_appointments_active_doctor_slot", table_name="appointments")
    op.drop_index("ix_appointments_slot", table_name="appointments")
    op.drop_index("ix_appointments_doctor_id", table_name="appointments")
    op.drop_table("appointments")
    op.drop_table("doctors")
