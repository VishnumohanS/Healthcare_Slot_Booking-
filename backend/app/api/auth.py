from fastapi import APIRouter, status

from app.dependencies import CurrentUser, DbSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenRead, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession):
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenRead)
def login(payload: LoginRequest, db: DbSession):
    return auth_service.login(db, payload.username, payload.password)


@router.get("/me", response_model=UserRead)
def get_me(user: CurrentUser, db: DbSession):
    return auth_service.public_user(db, user)
