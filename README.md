# Healthcare Appointment Booking System

A complete, runnable appointment-booking application for Windows 10/11 (no Docker):

* **Backend** - FastAPI + Pydantic + SQLAlchemy 2 + SQLite, schema managed by Alembic.
* **Frontend** - React (JavaScript) + Vite + Axios + Chart.js.
* **SDK** - a Python client *generated* by OpenAPI Generator from the live `/openapi.json`.
* **Tests** - Pytest tests on a throw-away database.

## Contents
1. [Features](#features) - 2. [Architecture](#architecture) - 3. [Technology stack](#technology-stack) - 4. [Folder structure](#folder-structure) - 5. [Prerequisites](#prerequisites) - 6. [Install & run (Windows)](#install--run-windows) - 7. [Migrations & seed data](#migrations--seed-data) - 8. [Tests](#running-the-tests) - 9. [Python SDK](#python-sdk) - 10. [API reference](#api-reference) - 11. [Booking rules](#booking-rules-and-design-decisions) - 12. [Troubleshooting](#troubleshooting) - 13. [Limitations](#known-limitations-and-assumptions)

## Features
* Username/password registration and login for patients and doctors, with hashed passwords and role-protected API routes.
* Doctor profiles with editable working hours, specialization, description and consultation fees.
* Doctors can block their own slots, see their appointment list and view a Chart.js appointments/revenue dashboard.
* Patients can browse doctors, see live availability, pay the doctor's fee in Razorpay Test Mode, and cancel more than two hours before a booking.
* Payment-confirmed bookings, 15-minute unpaid checkout reservations and database-enforced slot uniqueness.
* Working-hours and slot-boundary enforcement; cancellation frees the slot.
* Uniform JSON error envelope; no stack traces, SQL or secrets are ever returned.
* React UI: doctor list, booking form with live slot availability, appointment table with cancel, loading / empty / error states, responsive layout, labelled & keyboard-friendly controls, 15-second polling refresh.

## Architecture
```
React (Vite, Axios) --HTTP/JSON--> FastAPI routes (app/api)
                                        |  thin: parse + document
                                        v
                                 Services (app/services)  <- all booking rules live here
                                        |
                                 SQLAlchemy models (app/models)
                                        |
                                   SQLite file  <- Alembic migrations create the schema
```
* Routes only validate/serialise; business rules (A-E below) sit in `services/`.
* One SQLAlchemy session per request via dependency injection (`dependencies.get_db`); tests override it.
* Errors are raised as domain errors and rendered by `core/error_handlers.py` in a single envelope:
  `{"error": {"code": "slot_already_booked", "message": "...", "details": null}}`.

## Technology stack
Python 3.11+ is supported. The backend uses FastAPI, SQLAlchemy, Alembic, PyJWT, pwdlib/Argon2 and the Razorpay Python SDK. The frontend uses React 18, Vite, Axios, Chart.js and react-chartjs-2.

## Folder structure
```
healthcare-appointment-system/
|-- setupdev.bat            one-time/re-runnable setup
|-- runapplication.bat      starts backend + frontend in two windows
|-- .env.example  .gitignore  openapitools.json  README.md
|-- backend/
|   |-- app/  main.py  dependencies.py
|   |   |-- core/      config.py  errors.py  error_handlers.py
|   |   |-- db/        base.py  session.py  seed.py
|   |   |-- models/    doctor.py  appointment.py
|   |   |-- schemas/   doctor.py  appointment.py  common.py
|   |   |-- api/       doctors.py  appointments.py  system.py
|   |   `-- services/  doctor_service.py  appointment_service.py
|   |-- alembic/ (env.py, versions/0001_initial_schema.py)  alembic.ini
|   |-- tests/ (conftest.py, test_doctors.py, test_appointments.py)
|   |-- seed_data.sql  requirements.txt  pytest.ini  run.py
|-- frontend/  (Vite app: src/api, src/components, src/hooks, src/utils)
|-- health_sdk/            generated Python SDK
`-- scripts/  start_backend.bat  start_frontend.bat  generate_sdk.bat  sdk_smoke_test.py
```

## Prerequisites
* Windows 10/11, PowerShell or Command Prompt
* **Python 3.11+** (tick "Add python.exe to PATH") - https://www.python.org/downloads/
* **Node.js 20.19+ or 22.12+** (includes npm; required by the Vite 8 toolchain) - https://nodejs.org/
* *Only for SDK generation:* **Java 11+** (e.g. Temurin) - https://adoptium.net/

## Install & run (Windows)
```bat
cd healthcare-appointment-system
setupdev.bat
runapplication.bat
```
`setupdev.bat` checks Python/Node, creates `.venv` (only if missing), installs dependencies, copies `.env.example` to `.env` (only if missing), runs `alembic upgrade head`, loads sample data (only if no doctors exist) and runs `npm install`. It stops on the first failing step and is safe to re-run; it never deletes your database.

`runapplication.bat` verifies the setup, then opens two windows ("Healthcare API" and "Healthcare Frontend"), so neither blocks the other.

| What | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI schema | http://127.0.0.1:8000/openapi.json |

Manual start (equivalent): `cd backend` -> `..\.venv\Scripts\python run.py`, and `cd frontend` -> `npm run dev`.

### Configuration (`.env`)
| Variable | Default | Meaning |
|---|---|---|
| `APP_ENV` | `development` | `production` rejects `CORS_ORIGINS=*` and disables auto-reload |
| `DATABASE_URL` | `sqlite:///./healthcare.db` | relative SQLite paths resolve against `backend/` |
| `BACKEND_HOST` / `BACKEND_PORT` | `127.0.0.1` / `8000` | where Uvicorn listens |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174` | allowed browser origins |
| `APPOINTMENT_DURATION_MINUTES` | `30` | slot length; must divide 60 |
| `SECRET_KEY` | development-only value | Set a long, random secret before deployment; required in production |
| `RAZORPAY_KEY_ID` | empty | Razorpay **Test Mode** key ID |
| `RAZORPAY_KEY_SECRET` | empty | Razorpay **Test Mode** secret; backend only, never prefix with `VITE_` |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | API URL used by the frontend |

If you change `BACKEND_PORT`, also update `VITE_API_BASE_URL` and restart Vite.

Create test API keys in the Razorpay Dashboard under **Account & Settings → API Keys → Test Mode**, then add them to the root `.env`. The UI opens Razorpay Checkout and the backend verifies its payment signature before marking an appointment booked. Without test keys, payment-order creation returns an explicit configuration error. Use Razorpay's documented test card details in the checkout.

Register a doctor through the app with a username, password, specialization, working hours and consultation fee. Register patient accounts separately. Existing seeded doctors remain publicly browseable, with the default consultation fee, but can only be edited after registration creates an account-linked profile.

## Migrations & seed data
Run from `backend/` with the venv active:
```bat
..\.venv\Scripts\activate
python -m alembic upgrade head          :: create / update the schema
python -m alembic downgrade base        :: drop everything (destructive)
python -m alembic revision --autogenerate -m "message"   :: after changing models
python -m app.db.seed                   :: load seed_data.sql (skipped if doctors exist)
python -m app.db.seed --force           :: re-apply; idempotent (INSERT OR IGNORE, fixed IDs)
```
**Seed data is applied after migrations** (the tables must exist). `seed_data.sql` inserts four doctors and four sample appointments dated "tomorrow" (one of them cancelled), and cannot violate any constraint. `setupdev.bat` runs it automatically on a fresh database.

## Running the tests
```bat
cd backend
..\.venv\Scripts\activate
python -m pytest
```
Tests build a temporary SQLite file using the real Alembic migrations and never touch the local database. Coverage includes account roles, appointment ownership, payment-order signature validation, working-hour/slot validation, cancellation limits, doctor profile/slot management and reports.

## Python SDK
The SDK in `health_sdk/` was produced by OpenAPI Generator 7.26.0 (`-g python`) from the running server's `/openapi.json`. Nothing in it was hand-written.

The checked-in generated client predates role authentication and paid booking; regenerate it before using it against the current API (backend must be running, Java installed):
```bat
runapplication.bat
scripts\generate_sdk.bat
python scripts\sdk_smoke_test.py
```
`generate_sdk.bat` runs `npx @openapitools/openapi-generator-cli generate -i http://127.0.0.1:8000/openapi.json -g python -o health_sdk --package-name health_sdk` (generator version pinned in `openapitools.json`) and then `pip install -e health_sdk`.

Do not use the checked-in client until it has been regenerated: its generated operations predate authentication, checkout, and the updated appointment workflow.

## API reference
Sign in with `POST /auth/login` or register with `POST /auth/register`, then send the returned token as `Authorization: Bearer <access_token>`. Open `/docs` for the complete request/response schema.

| Method & path | Access | Purpose |
|---|---|---|
| `POST /auth/register`, `POST /auth/login` | Public | Create account or sign in |
| `GET /auth/me` | Signed in | Current account |
| `GET /doctors/`, `GET /doctors/{id}` | Public | Browse doctor profiles |
| `GET /doctors/{id}/availability?date=YYYY-MM-DD` | Public | See occupied slot times (no patient details) |
| `GET /doctors/me`, `PATCH /doctors/me` | Doctor | Read/update own profile |
| `GET /doctors/me/reports` | Doctor | Own booking and revenue metrics |
| `POST /payments/orders`, `POST /payments/verify` | Patient | Create checkout/reservation and confirm a signed payment |
| `POST /payments/{appointment_id}/cancel` | Patient | Release an unpaid checkout reservation |
| `GET /appointments/` | Signed in | List only own appointments or doctor's schedule |
| `POST /appointments/block` | Doctor | Block a slot in own schedule |
| `DELETE /appointments/{id}` | Owner | Cancel an eligible patient booking or remove own block |
| `GET /health`, `GET /config/scheduling` | Public | Health and slot duration |

## Booking rules and design decisions
| Topic | Decision |
|---|---|
| **Slot length** | 30 minutes (`APPOINTMENT_DURATION_MINUTES`). Appointments must start on a multiple of the duration (09:00, 09:30, ...) with zero seconds. |
| **Working hours** | A doctor working 9-17 accepts starts from 09:00 to **16:30** inclusive. 08:30, 17:00 and 17:30 are rejected with 422 `outside_working_hours`; 09:15 is rejected with 422 `invalid_slot_boundary`. `end_hour` may be 24 (midnight). |
| **Time format & timezone** | `slot` is an ISO-8601 *clinic-local wall-clock* time with **no offset**, e.g. `2030-10-20T10:00:00`. `Z`/`+05:30` suffixes, date-only values, and timestamps are rejected (422). This removes ambiguous naive/aware comparisons; all comparisons use naive local times. Stored as `YYYY-MM-DD HH:MM:SS` text. |
| **Double booking** | A partial unique index `uq_appointments_active_doctor_slot` includes confirmed bookings, doctor blocks and pending payment reservations. |
| **Payment** | The server creates Razorpay INR orders using the doctor's fee in paise. A pending checkout reserves the slot for 15 minutes. The server verifies Razorpay's HMAC signature before confirming the booking. |
| **Cancellation** | Patients can cancel their own confirmed appointment only when it is more than two hours away. Cancelled rows are retained for history and release the slot. |
| **Doctor check** | Unknown doctor -> 404 (checked before hours/slot validation). |
| **Validation** | Unknown fields are rejected, strings are trimmed, names must be 1-100 chars, IDs must be integers >= 1, hours are strict integers. |
| **Past dates** | Rejected by the API. |

## Troubleshooting
| Symptom | Fix |
|---|---|
| `'python' is not recognized` | Reinstall Python with "Add to PATH"; reopen the terminal. |
| `setupdev.bat` says Python 3.11 needed | Install a newer Python; delete `.venv` and re-run. |
| `no such table` errors from the API | Run `python -m alembic upgrade head` in `backend/`. |
| Frontend shows "Cannot reach the server" | Start the backend; check `VITE_API_BASE_URL` and the port. |
| Browser console CORS error | Add the page's origin to `CORS_ORIGINS` and restart the backend. |
| Port 5173/8000 already in use | Close the other program or change `BACKEND_PORT` (and `VITE_API_BASE_URL`). Vite uses `strictPort`. |
| `database is locked` / 503 | Another process holds a long write transaction; close DB browsers and retry. |
| SDK generation: Java not found | Install Java 11+ and reopen the terminal. |
| `npm`/`npx` stops a batch script early | Use `call npm ...` inside `.bat` files (the provided scripts already do). |

## Known limitations and assumptions
* One fixed slot length for all doctors; no breaks, holidays or per-day schedules.
* No timezone support - appointment times use the server/clinic's local wall-clock time.
* Razorpay refunds are not automatic; configure a refund workflow separately if cancellations should return paid fees.
* SQLite handles modest write concurrency; for heavy multi-server deployments use PostgreSQL (the partial unique index is also supported there).
* Polling (15 s) is used instead of WebSockets for refreshing availability.
* The `.bat` scripts were written for Windows 10/11 but were **not executed** in the Linux environment where this project was built (see the verification notes delivered with the project).
