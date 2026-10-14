@echo off
setlocal EnableExtensions
REM ============================================================================
REM  generate_sdk.bat - generates ./health_sdk from the RUNNING backend's /openapi.json
REM  Prerequisites: backend running (runapplication.bat), Java 11+ on PATH, Node.js (for npx).
REM ============================================================================
cd /d "%~dp0.."
where java >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Java was not found. Install Java 11+ ^(e.g. Temurin: https://adoptium.net/^) and reopen this window.
    exit /b 1
)
".venv\Scripts\python.exe" -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/openapi.json', timeout=5)" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] http://127.0.0.1:8000/openapi.json is not reachable. Start the backend first ^(runapplication.bat^).
    exit /b 1
)
call npx --yes @openapitools/openapi-generator-cli@2.41.0 generate -i http://127.0.0.1:8000/openapi.json -g python -o health_sdk --package-name health_sdk --additional-properties=projectName=health-sdk,packageVersion=1.0.0
if errorlevel 1 (
    echo [ERROR] SDK generation failed.
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install -e health_sdk
if errorlevel 1 exit /b 1
echo.
echo SDK generated in .\health_sdk and installed. Smoke test:  python scripts\sdk_smoke_test.py
endlocal
