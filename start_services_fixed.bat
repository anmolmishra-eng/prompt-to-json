@echo off
echo ============================================
echo Starting BHIV AI Assistant - Fixed Version
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"
call venv\Scripts\activate.bat

echo.
echo Killing any existing services...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 2

echo.
echo Starting services in sequence...

REM Start Main Backend API first
echo [1/3] Starting Main Backend API (Port 8000)...
start "Main Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5

REM Start BHIV AI Assistant
echo [2/3] Starting BHIV AI Assistant (Port 8003)...
start "BHIV Assistant" cmd /k "cd app\bhiv_assistant && python start_bhiv.py"
timeout /t 3

REM Start Prefect Server on different port
echo [3/3] Starting Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"

echo.
echo ============================================
echo Services starting...
echo.
echo Access Points:
echo - Main API: http://localhost:8000/docs
echo - BHIV Assistant: http://localhost:8003
echo - Prefect UI: http://localhost:4201
echo.
echo Wait 30 seconds then press any key to test...
echo ============================================
timeout /t 30

echo Opening service URLs...
start http://localhost:8000/docs
start http://localhost:8003
start http://localhost:4201
