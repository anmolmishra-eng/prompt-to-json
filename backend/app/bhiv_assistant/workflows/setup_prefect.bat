@echo off
REM Setup Prefect for workflow orchestration

echo Setting up Prefect workflow orchestration...

REM Install Prefect
pip install prefect==2.14.3 prefect-docker==0.4.1 prefect-sqlalchemy==0.2.4

REM Set API URL
prefect config set PREFECT_API_URL="http://localhost:4200/api"

REM Create deployment directory structure
mkdir workflows\ingestion 2>nul
mkdir workflows\monitoring 2>nul
mkdir workflows\compliance 2>nul

echo [OK] Prefect packages installed
echo [OK] API URL configured
echo [OK] Workflow directories created
echo.
echo To start Prefect server:
echo   prefect server start
echo.
echo To create work pool:
echo   prefect work-pool create default-pool --type process
echo.
echo Server will be available at: http://localhost:4200