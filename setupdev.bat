@echo off
setlocal EnableExtensions
REM ============================================================================
REM  setupdev.bat - one-time (and safely re-runnable) development setup, Windows 10/11
REM  Never deletes an existing virtual environment, database or node_modules.
REM ============================================================================
cd /d "%~dp0"
echo.
echo === Healthcare Appointment Booking System - setup ===
echo.

echo [1/7] Checking prerequisites...
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH. Install Python 3.11+ from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH" during installation.
    goto :fail
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.11 or newer is required. Found:
    python --version
    goto :fail
)
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js was not found on PATH. Install the LTS release from https://nodejs.org/
    goto :fail
)
where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm was not found on PATH. Reinstall Node.js from https://nodejs.org/
    goto :fail
)
node -e "const [major,minor]=process.versions.node.split('.').map(Number);process.exit((major===20&&minor>=19)||(major===22&&minor>=12)||major>22?0:1)"
if errorlevel 1 (
    echo [ERROR] Node.js 20.19+ or 22.12+ is required by Vite 8.
    node --version
    goto :fail
)
python --version
node --version
call npm --version

echo.
echo [2/7] Python virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo     .venv already exists - reusing it.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        goto :fail
    )
    echo     Created .venv
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Could not activate the virtual environment.
    goto :fail
)

echo.
echo [3/7] Installing backend dependencies...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
python -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] Installing backend dependencies failed.
    goto :fail
)

echo.
echo [4/7] Environment file...
if exist ".env" (
    echo     .env already exists - leaving it unchanged.
) else (
    copy /y ".env.example" ".env" >nul
    if errorlevel 1 goto :fail
    echo     Created .env from .env.example
)

echo.
echo [5/7] Applying database migrations (alembic upgrade head)...
pushd backend
python -m alembic upgrade head
if errorlevel 1 (
    popd
    echo [ERROR] Database migration failed.
    goto :fail
)

echo.
echo [6/7] Loading sample data (skipped if doctors already exist)...
python -m app.db.seed
if errorlevel 1 (
    popd
    echo [ERROR] Seeding failed.
    goto :fail
)
popd

echo.
echo [7/7] Installing frontend dependencies (npm install)...
pushd frontend
call npm install
if errorlevel 1 (
    popd
    echo [ERROR] npm install failed.
    goto :fail
)
popd

echo.
echo ============================================================================
echo  SUCCESS - setup complete.
echo    Start the app :  runapplication.bat
echo    Run the tests :  .venv\Scripts\activate  then  cd backend  then  python -m pytest
echo ============================================================================
endlocal
exit /b 0

:fail
echo.
echo ============================================================================
echo  SETUP FAILED - fix the error above and run setupdev.bat again (it is safe to re-run).
echo ============================================================================
endlocal
exit /b 1
