@echo off
echo ============================================
echo BHIV AI Assistant - Event-Driven System
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
timeout /t 2

echo [1/6] Installing PyMuPDF for PDF processing...
pip install pymupdf

echo [2/6] Creating watch directories...
mkdir data\incoming 2>nul
mkdir data\incoming\processed 2>nul
mkdir data\logs 2>nul
mkdir data\reports 2>nul

echo [3/6] Starting Fast Main Server (Port 8000)...
start "Main API" cmd /k "python -m uvicorn app.main_fast:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [4/6] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 10

echo [5/6] Deploying Event-Driven Workflows...
cd app\bhiv_assistant\workflows
python deploy_event_flows.py
timeout /t 3

echo [6/6] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo Event-Driven System Started:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo.
echo Event-Driven Workflows:
echo - n8n-replacement-flow (replaces n8n automation)
echo - file-watcher-flow (processes new files)
echo - scheduled-maintenance-flow (system cleanup)
echo - webhook-triggered-flow (external events)
echo.
echo File Processing:
echo - Drop PDFs in: data/incoming/
echo - Drop GLB files in: data/incoming/
echo - Files auto-processed and archived
echo ============================================
timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
