#!/bin/bash
# Setup Prefect for workflow orchestration

echo "🚀 Setting up Prefect workflow orchestration..."

# Install Prefect
pip install prefect==2.14.3 prefect-docker==0.4.1 prefect-sqlalchemy==0.2.4

# Start Prefect server (alternative to Prefect Cloud)
echo "Starting Prefect server..."
prefect server start &

# Wait for server to be ready
sleep 10

# Create work pool
prefect work-pool create default-pool --type process

# Set API URL
prefect config set PREFECT_API_URL="http://localhost:4200/api"

echo "✅ Prefect server running at http://localhost:4200"
echo "✅ Work pool 'default-pool' created"

# Create deployment directory structure
mkdir -p workflows/{ingestion,monitoring,compliance}

echo "📂 Workflow directories created"