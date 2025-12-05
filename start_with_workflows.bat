@echo off
echo Starting BHIV System with Simple Workflows
echo ===========================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/4] Starting Main Backend API...
start "Main API" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [2/4] Starting BHIV Assistant...
start "BHIV Assistant" cmd /k "cd app\bhiv_assistant && python start_bhiv.py"
timeout /t 3

echo [3/4] Starting Prefect Server...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [4/4] Deploying Simple Workflows...
cd app\bhiv_assistant\workflows
python simple_deploy.py

echo.
echo Services started:
echo - Main API: http://localhost:8000/docs
echo - BHIV Assistant: http://localhost:8003
echo - Prefect UI: http://localhost:4201
echo.
timeout /t 5
start http://localhost:8000/docs
start http://localhost:8003
start http://localhost:4201
