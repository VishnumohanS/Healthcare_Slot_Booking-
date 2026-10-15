from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api import appointments, auth, doctors, payments, system
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers

import logging as _logging

_log = _logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI):  # noqa: ARG001
    """Startup checks — runs once before the server starts accepting requests."""
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        _log.warning(
            "RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET is not set. "
            "Payment endpoints will return 503 until both keys are added to .env."
        )
    yield

DESCRIPTION = """
Healthcare appointment booking API.

**Rules:** fixed-length slots (default 30 min) inside a doctor's working hours; a doctor can never have
two active appointments at the same time; cancelling frees the slot.
Times are clinic-local wall-clock values without a timezone offset (e.g. `2030-10-20T10:00:00`).
"""


def _operation_id(route: APIRoute) -> str:
    # Clean names (create_doctor, book_appointment, ...) give a readable generated SDK.
    return route.name


def create_app() -> FastAPI:
    app = FastAPI(
        title="Healthcare Appointment Booking API",
        version="1.0.0",
        description=DESCRIPTION,
        generate_unique_id_function=_operation_id,
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )
    register_exception_handlers(app)
    app.include_router(doctors.router)
    app.include_router(auth.router)
    app.include_router(appointments.router)
    app.include_router(payments.router)
    app.include_router(system.router)
    return app


app = create_app()
