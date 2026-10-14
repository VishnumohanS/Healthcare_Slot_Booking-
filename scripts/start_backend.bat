@echo off
title Healthcare API (FastAPI)
cd /d "%~dp0..\backend"
"%~dp0..\.venv\Scripts\python.exe" run.py
echo.
echo Backend stopped (exit code %errorlevel%).
pause
