#!/bin/bash

# Deployment script for multi-city backend

set -e

echo "Starting Multi-City Backend Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure."
    exit 1
fi

# Build and start services
echo "Building and starting services..."
docker-compose -f deployment/docker-compose.yml up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Run health checks
echo "Running health checks..."
curl -f http://localhost/health || {
    echo "Health check failed!"
    docker-compose -f deployment/docker-compose.yml logs
    exit 1
}

# Run validation tests
echo "Running validation tests..."
docker-compose -f deployment/docker-compose.yml exec backend python scripts/validate_city_data.py

echo "Deployment completed successfully!"
echo "Services available at:"
echo "  - API: http://localhost/api/v1/"
echo "  - Docs: http://localhost/docs"
echo "  - Health: http://localhost/health"