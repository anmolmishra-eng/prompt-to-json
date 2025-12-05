@echo off
echo ============================================
echo Starting BHIV AI Assistant - All Services
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo.
echo Starting services in separate windows...
echo.

REM Start Prefect Server
echo [1/5] Starting Prefect Server (Port 4200)...
start "Prefect Server" cmd /k "prefect server start"
timeout /t 5

REM Start Prefect Worker
echo [2/5] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"
timeout /t 3

REM Setup and Deploy Workflows
echo [3/5] Setting up Prefect workflows...
start "Setup Workflows" cmd /k "cd app\bhiv_assistant\workflows && python setup_prefect_complete.py && python deploy_all_flows.py"
timeout /t 5

REM Start Main Backend API
echo [4/5] Starting Main Backend API (Port 8000)...
start "Main Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3

REM Start BHIV AI Assistant
echo [5/5] Starting BHIV AI Assistant (Port 8003)...
start "BHIV Assistant" cmd /k "cd app\bhiv_assistant && python start_bhiv.py"

echo.
echo ============================================
echo All services starting...
echo.
echo Access Points:
echo - Main API: http://localhost:8000/docs
echo - BHIV Assistant: http://localhost:8003
echo - Prefect UI: http://localhost:4200
echo - Health Check: http://localhost:8000/api/v1/health
echo.
echo Press any key to open service URLs...
echo ============================================
pause

REM Open service URLs
start http://localhost:8000/docs
start http://localhost:8003
start http://localhost:4200

echo Services opened in browser!
