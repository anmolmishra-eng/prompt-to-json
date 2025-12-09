@echo off
echo ============================================
echo BHIV AI Assistant - Monitored System
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/6] Installing notification dependencies...
pip install prefect-slack
pip install prefect-email

echo [2/6] Creating monitoring directories...
mkdir data\alerts 2>nul
mkdir data\reports 2>nul
mkdir data\health 2>nul

echo [3/6] Starting Fast Main Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main_fast:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [4/6] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [5/6] Deploying All Workflows...
cd app\bhiv_assistant\workflows
python deploy_mcp_flows.py
python deploy_rl_integration.py
python deploy_notifications.py
timeout /t 5

echo [6/6] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo Monitored System Started:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo Monitoring Features:
echo - Slack notifications on failures
echo - Email alerts for critical errors
echo - System health monitoring
echo - Automatic retries with alerts
echo - Structured logging and audit trails
echo.
echo Deployed Workflows:
echo - monitored-rl-flow (RL with alerts)
echo - monitored-mcp-flow (MCP with alerts)
echo - system-health-monitoring (health checks)
echo - reliable-workflow-retries (retry logic)
echo.
echo Alert Logs:
echo - data/alerts/slack_notifications.jsonl
echo - data/alerts/email_notifications.jsonl
echo - data/reports/health_report.json
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
