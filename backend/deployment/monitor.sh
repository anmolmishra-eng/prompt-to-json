#!/bin/bash
# Monitor deployment status

echo "Monitoring Multi-City Backend..."

while true; do
    clear
    echo "=== Multi-City Backend Status ==="
    echo "Time: $(date)"
    echo ""

    # Service status
    echo "Services:"
    docker-compose -f deployment/docker-compose.yml ps
    echo ""

    # Health checks
    echo "Health Status:"
    ./deployment/health_check.sh 2>/dev/null || echo "Health checks failed"
    echo ""

    # Resource usage
    echo "Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo ""

    # Recent logs (last 5 lines)
    echo "Recent Backend Logs:"
    docker-compose -f deployment/docker-compose.yml logs --tail=5 backend

    sleep 30
done
