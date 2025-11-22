@echo off
echo 🚀 Setting up Task 8: BHIV AI Assistant Integration

REM Create new repo structure
mkdir bhiv-assistant
cd bhiv-assistant

REM Initialize directories
mkdir app\bhiv_layer
mkdir app\mcp
mkdir app\multi_city
mkdir app\geometry
mkdir app\integrations
mkdir workflows
mkdir deployment\staging
mkdir deployment\production
mkdir tests\unit
mkdir tests\integration
mkdir docs
mkdir reports

REM Create __init__.py files
echo. > app\__init__.py
echo. > app\bhiv_layer\__init__.py
echo. > app\mcp\__init__.py
echo. > app\multi_city\__init__.py
echo. > app\geometry\__init__.py
echo. > app\integrations\__init__.py
echo. > tests\__init__.py
echo. > tests\unit\__init__.py
echo. > tests\integration\__init__.py

REM Initialize git
git init
git remote add origin https://github.com/anmolmishra-eng/bhiv-assistant.git

REM Create requirements
(
echo # Core dependencies
echo fastapi==0.104.1
echo uvicorn[standard]==0.24.0
echo pydantic==2.5.0
echo sqlalchemy==2.0.23
echo alembic==1.13.0
echo.
echo # Workflow orchestration ^(Prefect instead of N8N^)
echo prefect==2.14.3
echo prefect-docker==0.4.1
echo prefect-sqlalchemy==0.2.4
echo.
echo # Task 7 integration
echo httpx==0.25.1
echo aiohttp==3.9.0
echo.
echo # Multi-agent systems
echo langchain==0.0.340
echo anthropic==0.7.0
echo.
echo # Geometry processing
echo trimesh==4.0.5
echo pygltflib==1.16.1
echo numpy==1.24.3
echo.
echo # MCP integration
echo pydantic-mcp==0.1.0
echo.
echo # Multi-city datasets
echo geopandas==0.14.0
echo shapely==2.0.2
echo.
echo # Testing
echo pytest==7.4.3
echo pytest-asyncio==0.21.1
echo pytest-cov==4.1.0
echo.
echo # Monitoring
echo sentry-sdk==1.38.0
echo prometheus-client==0.19.0
) > requirements.txt

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo ✅ Task 8 structure created!
echo 📂 Directory: %cd%
pause