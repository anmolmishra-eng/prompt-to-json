@echo off
echo ============================================
echo BHIV AI Assistant - Prefect-FastAPI Integration
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/5] Creating data directories...
mkdir data\feedback 2>nul
mkdir data\tasks 2>nul

echo [2/5] Starting Fast Main Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main_fast:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [3/5] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [4/5] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"
timeout /t 3

echo [5/5] Deploying Integration Workflows...
cd app\bhiv_assistant\workflows
python deploy_event_flows.py

echo.
echo ============================================
echo Prefect-FastAPI Integration Started:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo FastAPI Endpoints with Prefect:
echo - GET /prefect/rules (MCP rules)
echo - POST /prefect/submit (RL prompts via Prefect)
echo - GET /prefect/tasks/{id}/status (task polling)
echo - POST /prefect/feedback (feedback logging)
echo - GET /prefect/health (integration health)
echo.
echo BHIV Endpoints:
echo - POST /bhiv/v1/prompt (orchestrated)
echo - POST /bhiv/v1/feedback (logged)
echo - GET /bhiv/v1/health (status)
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
