@echo off
setlocal EnableExtensions
REM ============================================================================
REM  runapplication.bat - starts the FastAPI backend and the Vite frontend,
REM  each in its own console window, so neither blocks the other.
REM ============================================================================
cd /d "%~dp0"
echo.
echo === Healthcare Appointment Booking System - starting ===
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Run setupdev.bat first.
    goto :fail
)
".venv\Scripts\python.exe" -c "import fastapi, uvicorn, sqlalchemy, alembic" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Backend dependencies are missing. Run setupdev.bat first.
    goto :fail
)
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies are missing. Run setupdev.bat first.
    goto :fail
)
if not exist "backend\healthcare.db" (
    echo [ERROR] Database not found. Run setupdev.bat first to create and migrate it.
    goto :fail
)

REM Read host/port from .env (defaults apply when absent)
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if /i "%%A"=="BACKEND_HOST" set "BACKEND_HOST=%%B"
        if /i "%%A"=="BACKEND_PORT" set "BACKEND_PORT=%%B"
    )
)

echo Starting backend  (new window "Healthcare API")...
start "Healthcare API" "%~dp0scripts\start_backend.bat"
echo Starting frontend (new window "Healthcare Frontend")...
start "Healthcare Frontend" "%~dp0scripts\start_frontend.bat"

echo.
echo ============================================================================
echo  Frontend    : http://localhost:5173
echo  API         : http://%BACKEND_HOST%:%BACKEND_PORT%
echo  Swagger UI  : http://%BACKEND_HOST%:%BACKEND_PORT%/docs
echo  ReDoc       : http://%BACKEND_HOST%:%BACKEND_PORT%/redoc
echo  OpenAPI JSON: http://%BACKEND_HOST%:%BACKEND_PORT%/openapi.json
echo.
echo  Both servers keep running in their own windows. Close those windows (or press
echo  Ctrl+C in them) to stop the application.
echo ============================================================================
endlocal
exit /b 0

:fail
echo.
echo  Application not started.
endlocal
pause
exit /b 1
