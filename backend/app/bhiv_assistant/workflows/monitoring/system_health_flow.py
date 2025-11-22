"""
System Health Monitoring Flow
Monitors BHIV system components health
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

import httpx
from prefect import flow, task
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthConfig(BaseModel):
    """Configuration for health monitoring"""

    services: Dict[str, str] = {
        "task7": "http://localhost:8000/api/v1/health",
        "sohum_mcp": "https://ai-rule-api-w7z5.onrender.com/health",
        "ranjeet_rl": "https://api.yotta.com/health",
        "bhiv": "http://localhost:8003/bhiv/v1/health",
    }
    timeout: int = 10


@task(name="check-service-health")
async def check_service_health(service_name: str, health_url: str, timeout: int) -> Dict:
    """
    Check health of individual service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(health_url, timeout=timeout)

            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ {service_name} is healthy")

                return {
                    "service": service_name,
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "details": health_data,
                }
            else:
                logger.warning(f"⚠️ {service_name} returned {response.status_code}")

                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                }

    except httpx.TimeoutException:
        logger.error(f"❌ {service_name} timed out")
        return {"service": service_name, "status": "timeout", "error": "Request timed out"}

    except Exception as e:
        logger.error(f"❌ {service_name} failed: {e}")
        return {"service": service_name, "status": "error", "error": str(e)}


@task(name="generate-health-report")
def generate_health_report(health_results: List[Dict]) -> Dict:
    """
    Generate system health report
    """
    healthy_services = [r for r in health_results if r["status"] == "healthy"]
    unhealthy_services = [r for r in health_results if r["status"] != "healthy"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_services": len(health_results),
        "healthy_count": len(healthy_services),
        "unhealthy_count": len(unhealthy_services),
        "system_status": "healthy" if len(unhealthy_services) == 0 else "degraded",
        "services": health_results,
    }

    logger.info(f"System Health: {report['healthy_count']}/{report['total_services']} services healthy")

    return report


@flow(name="system-health-monitoring", description="Monitor health of all BHIV system components", version="1.0")
async def system_health_flow(config: HealthConfig = HealthConfig()):
    """
    Main health monitoring flow
    """
    logger.info("Starting system health monitoring...")

    # Check health of all services concurrently
    health_checks = []
    for service_name, health_url in config.services.items():
        health_check = check_service_health(service_name, health_url, config.timeout)
        health_checks.append(health_check)

    # Wait for all health checks to complete
    health_results = await asyncio.gather(*health_checks)

    # Generate health report
    health_report = generate_health_report(health_results)

    logger.info("System health monitoring complete")

    return health_report


if __name__ == "__main__":
    asyncio.run(system_health_flow())
