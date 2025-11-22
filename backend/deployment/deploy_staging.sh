#!/bin/bash
# Deploy to staging environment

echo "Deploying to STAGING environment..."

# Configuration
export ENVIRONMENT=staging
export COMPOSE_PROJECT_NAME=backend_staging

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f deployment/docker-compose.yml down

# Build images
echo "Building Docker images..."
docker-compose -f deployment/docker-compose.yml build --no-cache

# Start services
echo "Starting services..."
docker-compose -f deployment/docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run health checks
echo "Running health checks..."
./deployment/health_check.sh

# Run validation tests
echo "Running validation tests..."
docker-compose -f deployment/docker-compose.yml exec backend python scripts/validate_city_data.py

echo "Staging deployment complete!"
echo "API: http://localhost/api/v1/"
echo "Docs: http://localhost/docs"