"""
External Services Integration Module
Handles all external service calls with robust error handling, health checks, and fallbacks
"""
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ExternalServiceManager:
    """Manages external service integrations with health monitoring and fallbacks"""

    def __init__(self):
        self.service_health = {}
        self.last_health_check = {}
        self.health_check_interval = 300  # 5 minutes

    async def check_service_health(self, service_name: str, url: str, timeout: int = 10) -> ServiceStatus:
        """Check health of external service"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Try health endpoint first
                health_endpoints = ["/health", "/status", "/ping", "/_health"]

                for endpoint in health_endpoints:
                    try:
                        response = await client.get(f"{url.rstrip('/')}{endpoint}")
                        if response.status_code == 200:
                            self.service_health[service_name] = ServiceStatus.HEALTHY
                            self.last_health_check[service_name] = datetime.now()
                            logger.info(f"Service {service_name} is healthy")
                            return ServiceStatus.HEALTHY
                    except:
                        continue

                # If no health endpoint, try root
                response = await client.get(url)
                if response.status_code < 500:
                    self.service_health[service_name] = ServiceStatus.DEGRADED
                    self.last_health_check[service_name] = datetime.now()
                    logger.warning(f"Service {service_name} is degraded (no health endpoint)")
                    return ServiceStatus.DEGRADED

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")

        self.service_health[service_name] = ServiceStatus.UNHEALTHY
        self.last_health_check[service_name] = datetime.now()
        return ServiceStatus.UNHEALTHY

    def should_use_service(self, service_name: str) -> bool:
        """Determine if service should be used based on health"""
        status = self.service_health.get(service_name, ServiceStatus.UNKNOWN)
        last_check = self.last_health_check.get(service_name)

        # If never checked, try the service (optimistic approach)
        if not last_check:
            return True

        # If check is stale, try the service again
        if datetime.now() - last_check > timedelta(seconds=self.health_check_interval):
            return True

        # Only avoid service if explicitly unhealthy
        return status != ServiceStatus.UNHEALTHY


# Global service manager instance
service_manager = ExternalServiceManager()


class SohumMCPClient:
    """Client for Sohum's MCP compliance system"""

    def __init__(self):
        self.base_url = settings.SOHUM_MCP_URL
        self.api_key = settings.SOHUM_API_KEY
        self.timeout = settings.SOHUM_TIMEOUT

    async def health_check(self) -> ServiceStatus:
        """Check MCP service health"""
        return await service_manager.check_service_health("sohum_mcp", self.base_url, self.timeout)

    async def run_compliance_case(self, case_data: Dict) -> Dict:
        """Run compliance analysis case"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Format data for Sohum's API
            formatted_data = {
                "project_id": case_data.get("project_id", "unknown_project"),
                "case_id": case_data.get(
                    "case_id", f"case_{case_data.get('city', 'mumbai').lower()}_{hash(str(case_data)) % 10000}"
                ),
                "city": case_data.get("city", "Mumbai"),
                "document": f"{case_data.get('city', 'Mumbai')}_DCR.pdf",
                "parameters": case_data.get("parameters", {}),
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/run_case", json=formatted_data, headers=headers)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.warning(f"MCP service timeout after {self.timeout}s")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP service HTTP error: {e.response.status_code if e.response else 'unknown'}")
            raise
        except Exception as e:
            logger.error(f"MCP service error: {e}")
            raise

    async def submit_feedback(self, feedback_data: Dict) -> Dict:
        """Submit compliance feedback"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/compliance/feedback", json=feedback_data, headers=headers
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"MCP feedback error: {e}")
            raise

    def get_mock_compliance_response(self, case_data: Dict) -> Dict:
        """Generate mock compliance response when service unavailable"""
        city = case_data.get("city", "Mumbai").lower()
        project_id = case_data.get("project_id", "unknown_project")

        city_rules = {
            "mumbai": ["MUM-FSI-URBAN-R15-20", "MUM-SETBACK-R15-20", "MUM-HEIGHT-STANDARD"],
            "pune": ["PUNE-HEIGHT-SPECIAL-ECO", "PUNE-FSI-SUBURBAN", "PUNE-SETBACK-ECO"],
            "ahmedabad": ["AMD-FSI-URBAN-R15-20", "AMD-SETBACK-R15-20", "AMD-HEIGHT-HERITAGE"],
            "nashik": ["NAS-FSI-SUBURBAN-R10-15", "NAS-SETBACK-R10-15", "NAS-HEIGHT-WINE-TOURISM"],
        }

        return {
            "project_id": project_id,
            "case_id": f"{city}_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "city": case_data.get("city", "Mumbai"),
            "parameters": case_data.get("parameters", {}),
            "rules_applied": city_rules.get(city, city_rules["mumbai"]),
            "reasoning": f"Mock compliance analysis for {city} - external service unavailable",
            "confidence_score": 0.3,
            "confidence_level": "Low",
            "confidence_note": "Mock response - external compliance service unavailable",
            "compliant": True,
            "violations": [],
            "geometry_url": None,
            "mock_response": True,
        }


class RanjeetRLClient:
    """Client for Ranjeet's RL optimization system"""

    def __init__(self):
        self.base_url = settings.RANJEET_RL_URL
        self.api_key = settings.RANJEET_API_KEY
        self.timeout = settings.RANJEET_TIMEOUT

    async def health_check(self) -> ServiceStatus:
        """Check RL service health"""
        return await service_manager.check_service_health("ranjeet_rl", self.base_url, self.timeout)

    async def optimize_design(self, spec_json: Dict, city: str, constraints: Dict = None) -> Dict:
        """Optimize design using RL"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {"spec_json": spec_json, "city": city, "constraints": constraints or {}}

            # Try different endpoint paths
            endpoints = ["/rl/optimize", "/optimize", "/api/rl/optimize"]

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for endpoint in endpoints:
                    try:
                        response = await client.post(f"{self.base_url}{endpoint}", json=payload, headers=headers)
                        response.raise_for_status()
                        return response.json()
                    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 404:
                            continue  # Try next endpoint
                        elif isinstance(e, httpx.ConnectError):
                            raise  # Connection failed, don't try other endpoints
                        else:
                            raise

                # If all endpoints failed with 404, raise error
                raise httpx.HTTPStatusError("All endpoints returned 404", request=None, response=None)

        except httpx.TimeoutException:
            logger.warning(f"RL service timeout after {self.timeout}s")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"RL service HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"RL service error: {e}")
            raise

    async def predict_reward(self, spec_json: Dict, prompt: str) -> Dict:
        """Predict reward for design"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {"spec_json": spec_json, "prompt": prompt}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/rl/predict", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"RL prediction error: {e}")
            raise

    def get_mock_rl_response(self, spec_json: Dict, city: str) -> Dict:
        """Generate mock RL response when service unavailable"""
        return {
            "optimized_layout": {
                "layout_type": "optimized",
                "efficiency_score": 0.85,
                "space_utilization": 0.82,
                "cost_optimization": 0.78,
                "city": city,
                "optimization_notes": f"Mock RL optimization for {city}",
            },
            "confidence": 0.3,
            "reward_score": 0.75,
            "status": "mock",
            "processing_time_ms": 50,
            "mock_response": True,
        }


# Global client instances
sohum_client = SohumMCPClient()
ranjeet_client = RanjeetRLClient()


async def initialize_external_services():
    """Initialize and health check all external services"""
    logger.info("Initializing external services...")

    # Check Sohum MCP
    sohum_status = await sohum_client.health_check()
    logger.info(f"Sohum MCP status: {sohum_status}")

    # Check Ranjeet RL
    ranjeet_status = await ranjeet_client.health_check()
    logger.info(f"Ranjeet RL status: {ranjeet_status}")

    return {"sohum_mcp": sohum_status, "ranjeet_rl": ranjeet_status}


async def get_service_health_status() -> Dict:
    """Get current health status of all external services"""
    return {
        "sohum_mcp": {
            "status": service_manager.service_health.get("sohum_mcp", ServiceStatus.UNKNOWN),
            "last_check": service_manager.last_health_check.get("sohum_mcp"),
            "url": settings.SOHUM_MCP_URL,
            "available": service_manager.should_use_service("sohum_mcp"),
        },
        "ranjeet_rl": {
            "status": service_manager.service_health.get("ranjeet_rl", ServiceStatus.UNKNOWN),
            "last_check": service_manager.last_health_check.get("ranjeet_rl"),
            "url": settings.RANJEET_RL_URL,
            "available": service_manager.should_use_service("ranjeet_rl"),
        },
    }


# Background task to periodically check service health
async def periodic_health_check():
    """Background task to check service health periodically"""
    while True:
        try:
            await initialize_external_services()
            await asyncio.sleep(service_manager.health_check_interval)
        except Exception as e:
            logger.error(f"Periodic health check failed: {e}")
            await asyncio.sleep(60)  # Retry in 1 minute on error
