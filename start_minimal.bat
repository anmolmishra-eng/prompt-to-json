@echo off
echo Starting BHIV System - Minimal Version
echo ========================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo Cleaning up processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 2

echo [1/2] Starting Main Backend API...
start "Main API" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

echo [2/2] Starting BHIV Assistant...
start "BHIV Assistant" cmd /k "cd app\bhiv_assistant && python start_bhiv.py"

echo.
echo Services started:
echo - Main API: http://localhost:8000/docs
echo - BHIV Assistant: http://localhost:8003
echo.
timeout /t 10
start http://localhost:8000/docs
start http://localhost:8003
