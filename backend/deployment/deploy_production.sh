#!/bin/bash
# Deploy to production environment

echo "DEPLOYING TO PRODUCTION"
echo "======================="
echo ""
echo "WARNING: This will deploy to production!"
echo "Ensure all tests have passed before proceeding."
echo ""

read -p "Have all final tests passed? (yes/no): " tests_passed

if [ "$tests_passed" != "yes" ]; then
    echo "Production deployment cancelled - tests not passing"
    exit 1
fi

echo ""
read -p "Enter production domain (e.g., api.company.com): " prod_domain

if [ -z "$prod_domain" ]; then
    echo "Production domain required"
    exit 1
fi

echo ""
echo "PRODUCTION DEPLOYMENT CHECKLIST"
echo "==============================="
echo ""
echo "Deploying to: $prod_domain"
echo "Environment: PRODUCTION"
echo ""

# Set production environment
export ENVIRONMENT=production
export COMPOSE_PROJECT_NAME=backend_production
export DOMAIN=$prod_domain

# Create backup
echo "Creating backup of current production..."
if [ -d "backups" ]; then
    mkdir -p backups
fi

# Build Docker images
echo ""
echo "Building production Docker images..."
docker-compose -f deployment/docker-compose.yml build --no-cache

# Stop current production
echo ""
echo "Stopping current production services..."
docker-compose -f deployment/docker-compose.yml down

# Start new production
echo ""
echo "Starting production services..."
docker-compose -f deployment/docker-compose.yml up -d

# Wait for services
echo ""
echo "Waiting for services to be ready (30 seconds)..."
sleep 30

# Health check
echo ""
echo "Running production health checks..."
./deployment/health_check.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "PRODUCTION DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "Service URLs:"
    echo "   API: https://$prod_domain/api/v1/"
    echo "   Docs: https://$prod_domain/docs"
    echo "   Health: https://$prod_domain/api/v1/health"
    echo ""
    echo "Next steps:"
    echo "   1. Monitor logs: docker-compose logs -f"
    echo "   2. Run smoke tests: python scripts/mock_smoke_tests.py"
    echo "   3. Notify team of deployment"
    echo ""
else
    echo ""
    echo "PRODUCTION DEPLOYMENT FAILED!"
    echo ""
    echo "Rolling back..."
    docker-compose -f deployment/docker-compose.yml down
    echo "Rollback complete - check logs for issues"
    exit 1
fi