from collections.abc import Iterator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def get_db() -> Iterator[Session]:
    """Yield one SQLAlchemy session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: DbSession,
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to access this resource.")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Your session is invalid or has expired.") from exc
    user = db.get(User, user_id)
    if user is None or user.role != payload.get("role"):
        raise HTTPException(status_code=401, detail="Your session is invalid or has expired.")
    return user


def require_role(role: str):
    def _require_role(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != role:
            raise HTTPException(status_code=403, detail=f"This action requires the {role} role.")
        return user

    return _require_role


CurrentUser = Annotated[User, Depends(get_current_user)]
PatientUser = Annotated[User, Depends(require_role("patient"))]
DoctorUser = Annotated[User, Depends(require_role("doctor"))]
