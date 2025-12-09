@echo off
echo ============================================
echo BHIV AI Assistant - Minimal Prefect Server
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/4] Starting Main FastAPI Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [2/4] Starting Minimal Prefect Server (Port 4201)...
start "Minimal Prefect" cmd /k "python app\bhiv_assistant\config\prefect_startup.py"
timeout /t 10

echo [3/4] Creating Work Pool...
prefect work-pool create default-pool --type process 2>nul

echo [4/4] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo Minimal BHIV System Started:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo Essential Prefect Endpoints Only:
echo - Flow management (/api/flows/)
echo - Flow runs (/api/flow_runs/)
echo - Task runs (/api/task_runs/)
echo - Deployments (/api/deployments/)
echo - Work pools (/api/work_pools/)
echo - Health checks (/api/health)
echo - Logs (/api/logs/)
echo.
echo Removed Unnecessary Endpoints:
echo - Block types/documents
echo - Concurrency limits
echo - Artifacts
echo - Variables
echo - Events
echo - Automations
echo - Collections
echo - Admin functions
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
