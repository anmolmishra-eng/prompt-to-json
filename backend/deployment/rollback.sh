#!/bin/bash
# Rollback to previous version

echo "Rolling back to previous version..."

# Get previous image
PREVIOUS_IMAGE=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep multi-city-backend | head -2 | tail -1)

if [ -z "$PREVIOUS_IMAGE" ]; then
    echo "No previous image found!"
    exit 1
fi

echo "Rolling back to: $PREVIOUS_IMAGE"

# Update docker-compose to use previous image
sed -i "s|image: multi-city-backend:latest|image: $PREVIOUS_IMAGE|g" deployment/docker-compose.yml

# Restart services
docker-compose -f deployment/docker-compose.yml up -d backend

# Wait and check health
sleep 30
./deployment/health_check.sh

echo "Rollback complete!"