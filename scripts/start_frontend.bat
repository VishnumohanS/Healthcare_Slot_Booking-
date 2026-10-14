@echo off
title Healthcare Frontend (Vite)
cd /d "%~dp0..\frontend"
call npm run dev
echo.
echo Frontend stopped (exit code %errorlevel%).
pause
