from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserRead


def public_user(db: Session, user: User) -> UserRead:
    doctor = db.scalars(select(Doctor).where(Doctor.user_id == user.id)).first()
    return UserRead(
        id=user.id, username=user.username, name=user.name, role=user.role,
        doctor_id=doctor.id if doctor else None,
    )


def _session(db: Session, user: User) -> dict:
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": public_user(db, user)}


def register(db: Session, data: RegisterRequest) -> dict:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name,
        role=data.role,
    )
    db.add(user)
    try:
        db.flush()
        if data.role == "doctor":
            db.add(Doctor(
                user_id=user.id,
                name=data.name,
                specialization=data.specialization,
                start_hour=data.start_hour,
                end_hour=data.end_hour,
                fee_paise=data.fee_paise,
                bio=data.bio,
            ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("That username is already registered.", code="username_taken") from exc
    db.refresh(user)
    return _session(db, user)


def login(db: Session, username: str, password: str) -> dict:
    user = db.scalars(select(User).where(User.username == username)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Username or password is incorrect.", code="invalid_credentials")
    return _session(db, user)
