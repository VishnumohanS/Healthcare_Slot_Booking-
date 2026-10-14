from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.dependencies import DbSession
from app.schemas.common import HealthResponse, SchedulingConfig

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, summary="Liveness and database check")
def health_check(db: DbSession):
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok")


@router.get(
    "/config/scheduling",
    response_model=SchedulingConfig,
    summary="Scheduling configuration",
    description="Lets clients (e.g. the React app) derive slots with the same duration the server enforces.",
)
def get_scheduling_config():
    return SchedulingConfig(slot_duration_minutes=settings.appointment_duration_minutes)
