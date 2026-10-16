# Healthcare Appointment Booking System — Setup & Run Guide

Welcome to the **Healthcare Appointment Booking System**, a full-stack, production-ready appointment scheduling and consultation management application built with **FastAPI**, **React (Vite)**, **SQLAlchemy**, **SQLite**, and **Razorpay** payment gateway integration.

This guide provides complete, step-by-step instructions to set up, configure, and run the project, including how to generate and configure your **Razorpay Test Mode API Keys**.

---

## Table of Contents

1. [Project Overview & Key Features](#1-project-overview--key-features)
2. [Architecture & Technology Stack](#2-architecture--technology-stack)
3. [Folder & Repository Structure](#3-folder--repository-structure)
4. [Prerequisites & System Requirements](#4-prerequisites--system-requirements)
5. [🔑 Razorpay Setup: How to Get Key ID & Secret Key](#5--razorpay-setup-how-to-get-key-id--secret-key)
6. [🚀 Quick Start (Automated Windows Setup)](#6--quick-start-automated-windows-setup)
7. [🛠️ Manual Setup Guide (Windows, macOS & Linux)](#7-️-manual-setup-guide-windows-macos--linux)
   - [Step 1: Environment File Configuration (`.env`)](#step-1-environment-file-configuration-env)
   - [Step 2: Backend Virtual Environment & Dependencies](#step-2-backend-virtual-environment--dependencies)
   - [Step 3: Database Migrations & Initial Seeding](#step-3-database-migrations--initial-seeding)
   - [Step 4: Frontend Dependencies & Build](#step-4-frontend-dependencies--build)
   - [Step 5: Starting the Development Servers](#step-5-starting-the-development-servers)
8. [🌐 Application Access & Interactive Documentation](#8--application-access--interactive-documentation)
9. [⚙️ Environment Variables Reference (`.env`)](#9-️-environment-variables-reference-env)
10. [👥 User Workflows & Testing Accounts](#10--user-workflows--testing-accounts)
11. [🧪 Running Automated Tests](#11--running-automated-tests)
12. [📦 Generating the Python Client SDK](#12--generating-the-python-client-sdk)
13. [🩺 Business Rules & Design Constraints](#13--business-rules--design-constraints)
14. [🧰 Troubleshooting & FAQs](#14--troubleshooting--faqs)

---

## 1. Project Overview & Key Features

The system connects doctors and patients with real-time schedule management, online payment collection, and analytical insights.

### 🌟 Core Capabilities
- **Role-Based Authentication**: Secure registration and login for both **Patients** and **Doctors** using JWT (JSON Web Tokens) with Argon2 password hashing.
- **Doctor Profiles & Working Hours**: Doctors can define their consultation fee (in INR), specialization, bio, and operational working hours (e.g., 09:00 to 17:00).
- **Live Slot Availability**: Real-time slot calculation adhering to 30-minute boundaries; prevents overlaps, double-bookings, or appointments outside working hours.
- **Schedule Blocking**: Doctors can block custom time slots for personal breaks, surgeries, or holidays.
- **Online Consultation Payment (Razorpay)**:
  - Generates Razorpay checkout orders for consultation fees.
  - Holds a **15-minute temporary reservation** during payment processing.
  - Server-side cryptographic HMAC-SHA256 signature verification before booking confirmation.
- **Patient Appointments & Cancellation**: Patients can view their appointments and cancel bookings up to 2 hours before the scheduled time (frees the slot automatically).
- **Doctor Analytics Dashboard**: Visual charts powered by Chart.js displaying appointment counts and total revenue metrics.
- **Client SDK & Open APIs**: Automatic OpenAPI schema with interactive Swagger/ReDoc docs and an auto-generated Python SDK client.

---

## 2. Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│               React + Vite Frontend (SPA)              │
│  (Axios, Chart.js, React-ChartJS-2, Razorpay Checkout) │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP REST (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend Server                │
│  (Pydantic, Dependency Injection, Argon2 Auth, JWT)    │
└────────────┬─────────────────────────────┬─────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│    SQLite Database      │   │  Razorpay Payment API    │
│  (SQLAlchemy 2 Alembic) │   │ (Test Mode Order/Verify) │
└─────────────────────────┘   └──────────────────────────┘
```

- **Backend**: Python 3.11+, FastAPI 0.143+, SQLAlchemy 2.0+, Alembic 1.20+, Pydantic v2, Uvicorn, Razorpay Python SDK.
- **Frontend**: React 18, Vite 8, Axios, Chart.js, React-Chartjs-2.
- **Database**: SQLite (managed with Alembic schema migrations).
- **Payments**: Razorpay Standard Checkout & Orders API.

---

## 3. Folder & Repository Structure

The core project code is located in the `healthcare-appointment-system/` directory:

```text
healthcare-appointment-system/
├── readme.md                           <-- Main project setup documentation (this file)
└── healthcare-appointment-system/      <-- Main project workspace directory
    ├── .env.example                    <-- Template for environment settings
    ├── .env                            <-- Application configuration (created from .env.example)
    ├── setupdev.bat                    <-- One-click automated setup script for Windows
    ├── runapplication.bat              <-- One-click application launcher for Windows
    ├── openapitools.json               <-- OpenAPI generator configuration
    │
    ├── backend/                        <-- FastAPI Python Backend
    │   ├── app/
    │   │   ├── api/                    <-- API route controllers (auth, doctors, appointments, payments)
    │   │   ├── core/                   <-- Config, security, error handlers
    │   │   ├── db/                     <-- Database session & seed script (seed.py)
    │   │   ├── models/                 <-- SQLAlchemy ORM models (User, Doctor, Appointment, Payment)
    │   │   ├── schemas/                <-- Pydantic validation schemas
    │   │   └── services/               <-- Business logic (booking, payments, availability)
    │   ├── alembic/                    <-- Alembic migration versions and config
    │   ├── tests/                      <-- Pytest test suite
    │   ├── seed_data.sql               <-- Initial sample doctors and appointments
    │   ├── requirements.txt            <-- Backend Python dependencies
    │   └── run.py                      <-- Backend direct entrypoint
    │
    ├── frontend/                       <-- React + Vite Frontend
    │   ├── src/
    │   │   ├── api/                    <-- Axios API client and endpoints
    │   │   ├── components/             <-- UI components (BookingForm, DoctorList, Dashboard, etc.)
    │   │   ├── hooks/                  <-- React authentication & data hooks
    │   │   └── utils/                  <-- Formatters, slot helpers, validators
    │   ├── index.html                  <-- App entry HTML (loads Razorpay checkout.js script)
    │   ├── package.json                <-- Frontend dependencies & npm scripts
    │   └── vite.config.js              <-- Vite configuration
    │
    ├── health_sdk/                     <-- Python client SDK generated from OpenAPI spec
    └── scripts/                        <-- Helper scripts (start_backend.bat, generate_sdk.bat, etc.)
```

---

## 4. Prerequisites & System Requirements

Before setting up the project, make sure you have the following installed on your machine:

1. **Python 3.11 or higher**:
   - Download from [python.org/downloads](https://www.python.org/downloads/).
   - ⚠️ **Important (Windows)**: Ensure you check the box **"Add python.exe to PATH"** during installation.
   - Verify in terminal:
     ```bash
     python --version
     ```
2. **Node.js (LTS version 20.19+ or 22.12+)**:
   - Download from [nodejs.org](https://nodejs.org/).
   - Includes `npm`.
   - Verify in terminal:
     ```bash
     node --version
     npm --version
     ```
3. **Web Browser**: Chrome, Edge, Firefox, or Safari with JavaScript enabled.
4. *(Optional - for generating SDK)* **Java 11+**:
   - Download [Eclipse Temurin](https://adoptium.net/) if you wish to run `scripts\generate_sdk.bat`.

---

## 5. 🔑 Razorpay Setup: How to Get Key ID & Secret Key

The booking workflow requires Razorpay API credentials to initiate orders and verify payment signatures. For local development and testing, use **Razorpay Test Mode** (100% free; no real charges occur).

### Step-by-Step Guide to Generate Test Keys

#### Step 1: Sign Up or Log In to Razorpay
1. Visit the [Razorpay Dashboard](https://dashboard.razorpay.com/).
2. Create an account or sign in with your existing credentials.

#### Step 2: Switch to Test Mode
1. After logging in, check the top bar or header on your Razorpay dashboard.
2. Toggle the switch from **Live Mode** to **Test Mode**.
3. When activated, a colored banner (usually orange/yellow) will state: **"Test Mode"**.

#### Step 3: Navigate to API Keys Settings
1. On the left navigation sidebar, click on **Account & Settings** (or the gear icon).
2. Under the **Developer Controls** or **Website and app settings** section, click on **API Keys**.
   - Direct link: [https://dashboard.razorpay.com/app/keys](https://dashboard.razorpay.com/app/keys)

#### Step 4: Generate Your Test API Keys
1. Click the **Generate Test Key** button (or **Regenerate Key** if you previously generated one).
2. A pop-up dialog will appear displaying two values:
   - **Key ID**: A string starting with `rzp_test_` (e.g., `rzp_test_1DP5mmOlF5G5ag`).
   - **Key Secret**: A 24-character random string (e.g., `s9df8s7df87sdf87sd98fsdf`).
3. ⚠️ **Crucial**: Copy or download the **Key Secret** immediately! Razorpay will not display the secret key again once you close this modal.

#### Step 5: Configure Keys in the `.env` File
Open the `.env` file located in `healthcare-appointment-system/healthcare-appointment-system/.env` and paste your credentials:

```ini
RAZORPAY_KEY_ID=rzp_test_YourKeyIdHere
RAZORPAY_KEY_SECRET=YourKeySecretHere
```

> **Security Note**:
> - Never prefix `RAZORPAY_KEY_SECRET` with `VITE_`.
> - Never commit your `.env` file to public GitHub repositories (it is included in `.gitignore`).

#### Step 6: How to Test Payments in the App
When booking an appointment on the frontend:
1. Select a Doctor, choose an available date, and pick a time slot.
2. Click **Book & Pay Fee**. The official **Razorpay Checkout** popup will appear.
3. In Test Mode, use Razorpay test card credentials:
   - **Card Number**: `4111 1111 1111 1111` (or any valid Visa/Mastercard test card)
   - **Expiry Date**: Any future date (e.g., `12/28`)
   - **CVV**: `123`
   - **OTP**: Enter any 4 or 6-digit number (e.g., `123456`) or click **"Success"** on the test screen.
4. Razorpay returns the signature to the frontend, which sends it to `/payments/verify`. The backend verifies the HMAC SHA-256 signature, commits the appointment as **confirmed**, and updates the UI!

---

## 6. 🚀 Quick Start (Automated Windows Setup)

If you are on Windows 10 or 11, automated batch scripts are provided to configure and start the entire project effortlessly:

### Step 1: Open Terminal in the Project Directory
Open **PowerShell** or **Command Prompt** and navigate into the inner project folder:
```cmd
cd healthcare-appointment-system\healthcare-appointment-system
```

### Step 2: Run the Setup Script
```cmd
setupdev.bat
```
`setupdev.bat` automatically:
1. Validates Python 3.11+ and Node.js LTS versions.
2. Creates the Python virtual environment (`.venv`) if not present.
3. Upgrades `pip` and installs all backend Python packages (`requirements.txt`).
4. Creates `.env` from `.env.example` (if missing).
5. Applies database schema migrations via `alembic upgrade head`.
6. Seeds initial doctors and sample appointments (`seed_data.sql`).
7. Installs frontend dependencies (`npm install` in `frontend/`).

### Step 3: Add Razorpay Test Keys
Open the generated `.env` file in `healthcare-appointment-system\healthcare-appointment-system\.env` in any text editor and fill in your `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` (see [Section 5](#5--razorpay-setup-how-to-get-key-id--secret-key)).

### Step 4: Run the Application
```cmd
runapplication.bat
```
This launches two separate terminal windows:
- **Healthcare API**: Running Uvicorn on `http://127.0.0.1:8000`
- **Healthcare Frontend**: Running Vite on `http://localhost:5173`

Open [http://localhost:5173](http://localhost:5173) in your browser!

---

## 7. 🛠️ Manual Setup Guide (Windows, macOS & Linux)

If you are on macOS/Linux or prefer setting up each component manually:

### Step 1: Environment File Configuration (`.env`)
Navigate to the project root:
```bash
cd healthcare-appointment-system/healthcare-appointment-system
cp .env.example .env
```
Edit `.env` and configure:
```ini
APP_ENV=development
DATABASE_URL=sqlite:///./healthcare.db
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
APPOINTMENT_DURATION_MINUTES=30
SECRET_KEY=replace-with-a-random-secret-key-at-least-32-chars
RAZORPAY_KEY_ID=rzp_test_YourKeyIdHere
RAZORPAY_KEY_SECRET=YourKeySecretHere
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Step 2: Backend Virtual Environment & Dependencies
From `healthcare-appointment-system/healthcare-appointment-system/`:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate virtual environment
# On Windows (cmd):
.venv\Scripts\activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# 3. Upgrade pip and install backend packages
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### Step 3: Database Migrations & Initial Seeding
With your virtual environment activated:

```bash
# Move to backend directory
cd backend

# Run database migrations to create SQLite tables
python -m alembic upgrade head

# Seed initial doctors and sample appointments
python -m app.db.seed

# Return to project root
cd ..
```

### Step 4: Frontend Dependencies & Build
From `healthcare-appointment-system/healthcare-appointment-system/`:

```bash
cd frontend
npm install
cd ..
```

### Step 5: Starting the Development Servers

#### Terminal 1 (Backend API):
```bash
cd healthcare-appointment-system/healthcare-appointment-system
# Make sure virtual environment is active
# On Windows: .venv\Scripts\activate | On macOS/Linux: source .venv/bin/activate
cd backend
python run.py
```
*The API will start at `http://127.0.0.1:8000` with hot reload enabled.*

#### Terminal 2 (Frontend UI):
```bash
cd healthcare-appointment-system/healthcare-appointment-system/frontend
npm run dev
```
*The Vite dev server will start at `http://localhost:5173`.*

---

## 8. 🌐 Application Access & Interactive Documentation

Once both servers are running, access the following endpoints:

| Service / Interface | URL | Description |
|---|---|---|
| **Frontend Application** | [http://localhost:5173](http://localhost:5173) | Main user interface for patients and doctors |
| **Backend REST API** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | Root health & system status |
| **Interactive Swagger UI** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Test every API endpoint interactively |
| **ReDoc Documentation** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Clean, read-only API specification |
| **OpenAPI Specification** | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) | Raw OpenAPI v3 JSON schema |

---

## 9. ⚙️ Environment Variables Reference (`.env`)

The single `.env` file in `healthcare-appointment-system/healthcare-appointment-system/.env` is read by both FastAPI and Vite:

| Variable | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production`. In production, wildcard CORS is rejected. |
| `DATABASE_URL` | `sqlite:///./healthcare.db` | SQLite connection URL (relative to `backend/`). |
| `BACKEND_HOST` | `127.0.0.1` | Host address Uvicorn listens on. |
| `BACKEND_PORT` | `8000` | Port Uvicorn listens on. |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed browser origins. |
| `APPOINTMENT_DURATION_MINUTES` | `30` | Slot duration in minutes (must divide 60 evenly: 10, 15, 20, 30, 60). |
| `SECRET_KEY` | *(development key)* | 32+ character random secret used for JWT signing and Argon2 hashing. |
| `RAZORPAY_KEY_ID` | `""` | Razorpay **Test Mode** API Key ID (starts with `rzp_test_`). |
| `RAZORPAY_KEY_SECRET` | `""` | Razorpay **Test Mode** API Secret Key. |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | The backend endpoint URL communicated to the React frontend. |

---

## 10. 👥 User Workflows & Testing Accounts

### 1. Pre-seeded Doctors
When `python -m app.db.seed` is executed, four doctors are seeded:
- **Dr. Asha Raman** (Cardiology, 09:00 - 17:00, Fee: ₹500)
- **Dr. Miguel Alvarez** (Pediatrics, 08:00 - 16:00, Fee: ₹500)
- **Dr. Priya Nair** (Dermatology, 10:00 - 18:00, Fee: ₹500)
- **Dr. Tomasz Kowalski** (Orthopedics, 09:00 - 13:00, Fee: ₹500)

*Note: Seeded doctors are publicly browseable for booking. To manage working hours or block slots for a doctor, register a new Doctor account.*

### 2. Registering a New Doctor Account
1. Open [http://localhost:5173](http://localhost:5173).
2. Click **Sign In / Register** in the top navigation.
3. Switch to **Register**, select **Role: Doctor**, and enter:
   - Username & Password
   - Full Name & Specialization
   - Working hours (e.g., Start: `09:00`, End: `17:00`)
   - Consultation Fee in INR (e.g., `800`)
4. As a doctor, you can:
   - View your schedule and patient bookings.
   - **Block Slots** for personal time off.
   - Access the **Reports Dashboard** (appointments chart and revenue breakdown).

### 3. Registering a Patient & Booking
1. Open [http://localhost:5173](http://localhost:5173) in an incognito window or log out.
2. Click **Register** as a **Patient**.
3. Choose a Doctor from the list, select a date (tomorrow or later), and pick an available slot.
4. Click **Book & Pay Fee**.
5. Complete payment using the Razorpay test card.
6. Check your booking in **My Appointments**. You can cancel appointments if more than 2 hours remain before the slot.

---

## 11. 🧪 Running Automated Tests

The backend includes comprehensive Pytest unit and integration tests covering authentication, slot boundary enforcement, payment verification, and schedule blocking.

To execute tests:

```bash
cd healthcare-appointment-system/healthcare-appointment-system/backend
..\.venv\Scripts\activate   # Windows
# source ../.venv/bin/activate  # macOS / Linux

python -m pytest
```

*Note: Tests run against an isolated in-memory or temporary SQLite database and will not overwrite your active `healthcare.db`.*

---

## 12. 📦 Generating the Python Client SDK

A fully-typed Python SDK (`health_sdk/`) is generated from the live `/openapi.json` using OpenAPI Generator.

If you modify API routes or schemas and wish to regenerate the client SDK:
1. Ensure **Java 11+** is installed and accessible on your PATH (`java -version`).
2. Start the backend (`runapplication.bat` or `python run.py`).
3. Run the generator script:
   ```cmd
   cd healthcare-appointment-system\healthcare-appointment-system
   scripts\generate_sdk.bat
   ```
4. Run the SDK smoke test to verify:
   ```cmd
   python scripts\sdk_smoke_test.py
   ```

---

## 13. 🩺 Business Rules & Design Constraints

| Rule / Feature | Constraint Specification |
|---|---|
| **Slot Boundaries** | Fixed 30-minute intervals (`09:00`, `09:30`, `10:00`, etc.). Intermediate times (e.g., `09:15`) are rejected with `422 invalid_slot_boundary`. |
| **Working Hours** | Doctors only accept appointments that end at or before their `end_hour`. For a doctor working 9:00 to 17:00, the last booking slot is `16:30`. |
| **Time Format** | Clinic-local wall-clock ISO-8601 strings without UTC offsets (e.g. `2026-10-20T10:00:00`). Prevents timezone conversion discrepancies. |
| **Double Booking Prevention** | Database partial unique index (`uq_appointments_active_doctor_slot`) ensures no two active bookings, blocks, or pending payment reservations can occupy the same doctor and slot. |
| **Payment Reservation Window** | Initiating checkout reserves the slot for **15 minutes**. If payment is not completed or is dismissed, the slot expires or is immediately released. |
| **Cancellation Policy** | Patients may only cancel appointments that are at least **2 hours** in the future. Cancelled appointments release the slot for other patients. |

---

## 14. 🧰 Troubleshooting & FAQs

### Q1: `Razorpay is not configured (503 Service Unavailable)`
- **Reason**: `RAZORPAY_KEY_ID` or `RAZORPAY_KEY_SECRET` in `.env` is empty.
- **Solution**: Follow [Section 5](#5--razorpay-setup-how-to-get-key-id--secret-key) to generate test keys on Razorpay dashboard, add them to `.env`, and restart the backend.

### Q2: `'python' is not recognized as an internal or external command`
- **Reason**: Python is not added to your system environment variables PATH.
- **Solution**: Re-run the Python installer, select **Modify**, and check **"Add Python to environment variables"**. Reopen your command prompt.

### Q3: `Node.js version error when running setupdev.bat`
- **Reason**: Vite 8 requires Node.js 20.19+ or 22.12+.
- **Solution**: Upgrade Node.js from [nodejs.org](https://nodejs.org/) to the latest LTS version.

### Q4: Frontend shows `Cannot reach the backend server`
- **Reason**: Backend API is not running or running on an unexpected port.
- **Solution**: Verify the backend is active at [http://127.0.0.1:8000](http://127.0.0.1:8000). Check `VITE_API_BASE_URL` in `.env` matches the backend host and port.

### Q5: CORS error in browser developer console
- **Reason**: Frontend origin is not listed in `CORS_ORIGINS`.
- **Solution**: Add your frontend URL (e.g., `http://localhost:5173`) to `CORS_ORIGINS` in `.env` and restart the backend.

### Q6: `database is locked` error (SQLite)
- **Reason**: Another process (e.g., DB Browser for SQLite or an unclosed Python session) has an exclusive write lock.
- **Solution**: Close any SQLite viewer software and retry the request.

---

### Need further assistance?
Review the backend API interactive docs at `http://127.0.0.1:8000/docs` or run tests with `python -m pytest` to inspect system behavior.
