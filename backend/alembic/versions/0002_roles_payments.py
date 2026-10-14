"""Add authenticated roles, paid appointments, and doctor-managed slots.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    sqlite = bind.dialect.name == "sqlite"
    if sqlite:
        bind.exec_driver_sql("PRAGMA foreign_keys=OFF")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.CheckConstraint("role IN ('patient', 'doctor')", name="ck_users_role"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_users_name_not_blank"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    with op.batch_alter_table("doctors") as batch:
        batch.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("fee_paise", sa.Integer(), server_default="50000", nullable=False))
        batch.add_column(sa.Column("bio", sa.Text(), server_default="", nullable=False))
        batch.create_foreign_key(
            "fk_doctors_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE"
        )
    op.create_index("ix_doctors_user_id", "doctors", ["user_id"], unique=True)

    op.drop_index("uq_appointments_active_doctor_slot", table_name="appointments")
    with op.batch_alter_table("appointments") as batch:
        batch.drop_constraint("ck_appointments_patient_not_blank", type_="check")
        batch.alter_column("patient_name", existing_type=sa.String(100), nullable=True)
        batch.add_column(sa.Column("patient_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("payment_expires_at", sa.DateTime(), nullable=True))
        batch.create_foreign_key(
            "fk_appointments_patient_id_users", "users", ["patient_id"], ["id"], ondelete="RESTRICT"
        )
        batch.drop_constraint("ck_appointments_status", type_="check")
        batch.create_check_constraint(
            "ck_appointments_status",
            "status IN ('booked', 'cancelled', 'blocked', 'payment_pending')",
        )
        batch.create_check_constraint(
            "ck_appointments_patient_not_blank",
            "patient_name IS NULL OR length(trim(patient_name)) > 0",
        )
    op.create_index(
        "uq_appointments_active_doctor_slot",
        "appointments",
        ["doctor_id", "slot"],
        unique=True,
        sqlite_where=sa.text("status IN ('booked', 'blocked', 'payment_pending')"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(100), nullable=False),
        sa.Column("payment_id", sa.String(100), nullable=True),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("appointment_id"),
        sa.UniqueConstraint("order_id"),
        sa.UniqueConstraint("payment_id"),
    )
    if sqlite:
        bind.exec_driver_sql("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    bind = op.get_bind()
    sqlite = bind.dialect.name == "sqlite"
    if sqlite:
        bind.exec_driver_sql("PRAGMA foreign_keys=OFF")
    op.drop_table("payments")
    op.drop_index("uq_appointments_active_doctor_slot", table_name="appointments")
    with op.batch_alter_table("appointments") as batch:
        batch.drop_constraint("ck_appointments_status", type_="check")
        batch.drop_constraint("ck_appointments_patient_not_blank", type_="check")
        batch.drop_constraint("fk_appointments_patient_id_users", type_="foreignkey")
        batch.drop_column("patient_id")
        batch.drop_column("payment_expires_at")
        batch.alter_column("patient_name", existing_type=sa.String(100), nullable=False)
        batch.create_check_constraint("ck_appointments_status", "status IN ('booked', 'cancelled')")
        batch.create_check_constraint(
            "ck_appointments_patient_not_blank", "length(trim(patient_name)) > 0"
        )
    op.create_index(
        "uq_appointments_active_doctor_slot",
        "appointments",
        ["doctor_id", "slot"],
        unique=True,
        sqlite_where=sa.text("status = 'booked'"),
    )
    op.drop_index("ix_doctors_user_id", table_name="doctors")
    with op.batch_alter_table("doctors") as batch:
        batch.drop_constraint("fk_doctors_user_id_users", type_="foreignkey")
        batch.drop_column("user_id")
        batch.drop_column("fee_paise")
        batch.drop_column("bio")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    if sqlite:
        bind.exec_driver_sql("PRAGMA foreign_keys=ON")
