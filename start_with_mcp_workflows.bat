@echo off
echo ============================================
echo BHIV AI Assistant with MCP Workflows
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/4] Starting Fast Main Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main_fast:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [2/4] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [3/4] Deploying MCP Workflows...
cd app\bhiv_assistant\workflows
python deploy_mcp_flows.py
timeout /t 3

echo [4/4] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo System Started with MCP Workflows:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo MCP Workflows Available:
echo - mcp-compliance-workflow
echo - log-aggregation-workflow
echo - geometry-verification-workflow
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
