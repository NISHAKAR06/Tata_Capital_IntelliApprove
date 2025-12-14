@echo off
REM Run IntelliApprove mock servers and main backend on Windows

REM Change to repo root
cd /d "%~dp0"

REM Start mock servers in a new window
start "Mock Servers" cmd /k "cd /d %~dp0backend && python -m scripts.run_mock_servers"

REM Small delay to let mocks start
timeout /t 5 >nul

REM Start FastAPI backend in another window
start "API Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

exit /b 0
