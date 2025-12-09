@echo off
echo ============================================
echo BHIV AI Assistant - Complete System
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/5] Starting Fast Main Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main_fast:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [2/5] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [3/5] Deploying MCP Workflows...
cd app\bhiv_assistant\workflows
python deploy_mcp_flows.py
timeout /t 3

echo [4/5] Deploying RL Workflows...
python deploy_rl_flows.py
timeout /t 3

echo [5/5] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo Complete BHIV System Started:
echo - Main API + BHIV: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo Available Workflows:
echo - mcp-compliance-workflow
echo - log-aggregation-workflow
echo - geometry-verification-workflow
echo - multi-city-rl-workflow
echo - rl-feedback-loop-workflow
echo.
echo BHIV API Endpoints:
echo - GET /bhiv/v1/health
echo - POST /bhiv/v1/prompt
echo - POST /bhiv/v1/feedback
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
