@echo off
echo ============================================
echo BHIV AI Assistant - Complete Setup Script
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"

echo.
echo [1/6] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/6] Installing main dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/6] Installing BHIV Assistant dependencies...
pip install -r app\bhiv_assistant\requirements.txt

echo.
echo [4/6] Installing workflow dependencies...
pip install -r app\bhiv_assistant\workflows\requirements.txt

echo.
echo [5/6] Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
) else (
    echo .env file already exists
)

echo.
echo [6/6] Creating required directories...
mkdir logs 2>nul
mkdir temp 2>nul
mkdir uploads 2>nul
mkdir cache 2>nul
mkdir data\geometry_outputs 2>nul
mkdir data\mcp_rules 2>nul

echo.
echo ============================================
echo Setup Complete! Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: start_all_services.bat
echo ============================================
pause
