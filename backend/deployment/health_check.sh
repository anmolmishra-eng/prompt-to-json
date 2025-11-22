#!/bin/bash
# Health check all services

echo "Checking service health..."

# Backend API
echo -n "Backend API: "
if curl -sf http://localhost/health > /dev/null; then
    echo "Healthy"
else
    echo "Unhealthy"
    exit 1
fi

# Database
echo -n "Database: "
if docker-compose -f deployment/docker-compose.yml exec db pg_isready -U user > /dev/null 2>&1; then
    echo "Healthy"
else
    echo "Unhealthy"
    exit 1
fi

# Redis
echo -n "Redis: "
if docker-compose -f deployment/docker-compose.yml exec redis redis-cli ping > /dev/null 2>&1; then
    echo "Healthy"
else
    echo "Unhealthy"
    exit 1
fi

echo "All services healthy!"
