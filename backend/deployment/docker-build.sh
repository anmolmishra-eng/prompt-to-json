#!/bin/bash

# Docker build script for multi-city backend

echo "Building Multi-City Backend Docker Image..."

# Build the image
docker build -t multi-city-backend:latest -f deployment/Dockerfile .

# Tag for different environments
docker tag multi-city-backend:latest multi-city-backend:production
docker tag multi-city-backend:latest multi-city-backend:staging

echo "Docker image built successfully!"
echo "Available tags:"
echo "  - multi-city-backend:latest"
echo "  - multi-city-backend:production"
echo "  - multi-city-backend:staging"

# Optional: Push to registry
# docker push multi-city-backend:latest