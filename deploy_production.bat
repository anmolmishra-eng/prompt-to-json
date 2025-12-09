@echo off
echo ============================================
echo BHIV AI Assistant - Production Deployment
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"

echo [1/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/6] Installing production dependencies...
pip install gunicorn
pip install prefect-slack
pip install prefect-email

echo [3/6] Creating production directories...
mkdir data\logs 2>nul
mkdir data\alerts 2>nul
mkdir data\reports 2>nul
mkdir data\incoming_pdfs 2>nul
mkdir data\compliance_output 2>nul
mkdir data\geometry 2>nul

echo [4/6] Starting Prefect Server...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [5/6] Deploying all workflows...
cd app\bhiv_assistant\workflows
python deploy_mcp_flows.py
python deploy_rl_flows.py
python deploy_monitoring.py
timeout /t 5

echo [6/6] Starting production services...
cd ..\..\..

REM Start main API with Gunicorn (production WSGI server)
start "Production API" cmd /k "python -m uvicorn app.main_fast:app --host 0.0.0.0 --port 8000 --workers 4"

REM Start Prefect Worker
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo Production Deployment Complete!
echo.
echo Services:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo Deployed Workflows:
echo - mcp-compliance-workflow
echo - log-aggregation-workflow
echo - geometry-verification-workflow
echo - multi-city-rl-workflow
echo - rl-feedback-loop-workflow
echo - mcp-workflow-with-alerts
echo - rl-workflow-with-alerts
echo - system-monitoring-workflow
echo.
echo Monitoring:
echo - Logs: data/logs/
echo - Alerts: data/alerts/
echo - Reports: data/reports/
echo ============================================

timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
