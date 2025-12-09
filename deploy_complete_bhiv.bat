@echo off
echo ============================================
echo BHIV AI Assistant - Complete Deployment
echo ============================================

cd /d "c:\Users\Anmol\Desktop\Backend\backend"

echo [1/8] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/8] Installing missing dependencies...
pip install pdfplumber PyPDF2 prefect-slack prefect-email

echo [3/8] Creating required directories...
mkdir data\geometry_outputs 2>nul
mkdir data\rl_feedback 2>nul
mkdir data\alerts 2>nul
mkdir data\reports 2>nul
mkdir data\logs 2>nul
mkdir data\pdfs\incoming 2>nul
mkdir data\compliance_output 2>nul

echo [4/8] Cleaning up processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 3

echo [5/8] Starting Main FastAPI Server (Port 8000)...
start "BHIV Main API" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 8

echo [6/8] Starting Minimal Prefect Server (Port 4201)...
start "Prefect Server" cmd /k "prefect server start --port 4201"
timeout /t 12

echo [7/8] Deploying All Workflows...
cd app\bhiv_assistant\workflows
python -c "
import asyncio
from mcp_compliance_flow import mcp_compliance_flow
from rl_integration_flows import rl_optimization_flow
from notification_flows import system_health_monitoring_flow

async def deploy_all():
    try:
        # Deploy MCP workflow
        await mcp_compliance_flow.to_deployment(
            name='mcp-compliance-flow',
            work_pool_name='default-pool'
        )
        print('✅ MCP workflow deployed')

        # Deploy RL workflow
        await rl_optimization_flow.to_deployment(
            name='rl-optimization-flow',
            work_pool_name='default-pool'
        )
        print('✅ RL workflow deployed')

        # Deploy monitoring workflow
        await system_health_monitoring_flow.to_deployment(
            name='system-health-flow',
            work_pool_name='default-pool'
        )
        print('✅ Monitoring workflow deployed')

    except Exception as e:
        print(f'❌ Deployment failed: {e}')

asyncio.run(deploy_all())
"

echo [8/8] Starting Prefect Worker...
start "Prefect Worker" cmd /k "prefect worker start --pool default-pool"

echo.
echo ============================================
echo BHIV Complete System Deployed Successfully!
echo ============================================
echo.
echo 🌐 Access Points:
echo - Main API: http://localhost:8000/docs
echo - Prefect UI: http://localhost:4201
echo - Health Check: http://localhost:8000/api/v1/health
echo.
echo 🚀 Features Available:
echo - MCP/BHIV AI assistant integration
echo - Prefect workflow automation (PDF→JSON, logging)
echo - Multi-city rule support & RL feedback loop
echo - Geometry (.GLB) output generation
echo - Structured logging & monitoring/alerts
echo.
echo 📁 Data Directories Created:
echo - data/geometry_outputs (GLB files)
echo - data/rl_feedback (RL training data)
echo - data/alerts (Slack/email notifications)
echo - data/reports (System health reports)
echo - data/logs (Application logs)
echo - data/pdfs/incoming (PDF processing)
echo - data/compliance_output (MCP results)
echo.
echo 🔧 Deployed Workflows:
echo - mcp-compliance-flow (PDF processing & compliance)
echo - rl-optimization-flow (RL training & optimization)
echo - system-health-flow (Monitoring & alerts)
echo ============================================

timeout /t 5
start http://localhost:8000/docs
start http://localhost:4201
