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

    async def check_service_health(self, service_name: str, url: str, timeout: int = 60) -> ServiceStatus:
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

            if all(k in case_data for k in ["project_id", "case_id", "city", "document", "parameters"]):
                formatted_data = case_data
            else:
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
                raw_response = response.json()

                # Parse and structure the response
                return self._parse_compliance_response(raw_response)

        except httpx.TimeoutException:
            logger.warning(f"MCP service timeout after {self.timeout}s")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP service HTTP error: {e.response.status_code if e.response else 'unknown'}")
            raise
        except Exception as e:
            logger.error(f"MCP service error: {e}")
            raise

    def _parse_compliance_response(self, raw_response: Dict) -> Dict:
        """Parse Sohum MCP response into structured format"""
        violations = []
        recommendations = []

        # Extract violations from rules_applied or reasoning
        rules_applied = raw_response.get("rules_applied", [])
        reasoning = raw_response.get("reasoning", "")
        clause_summaries = raw_response.get("clause_summaries", [])

        # Parse violations from clause summaries
        for clause in clause_summaries:
            if "violation" in clause.get("notes", "").lower() or "non-compliant" in clause.get("notes", "").lower():
                violations.append(
                    {
                        "rule_id": clause.get("clause_id", "UNKNOWN"),
                        "description": clause.get("quick_summary", "Compliance violation detected"),
                        "severity": "high" if "critical" in clause.get("notes", "").lower() else "medium",
                        "authority": clause.get("authority", "Municipal Authority"),
                    }
                )

        # Generate recommendations from reasoning
        if "review" in reasoning.lower():
            recommendations.append("Review and update design to meet compliance requirements")
        if "setback" in reasoning.lower():
            recommendations.append("Verify setback requirements for the specified location")
        if "fsi" in reasoning.lower() or "fsr" in reasoning.lower():
            recommendations.append("Check Floor Space Index (FSI) calculations")
        if "height" in reasoning.lower():
            recommendations.append("Ensure building height complies with zoning regulations")

        # Add rule-specific recommendations
        for rule in rules_applied:
            if "FSI" in rule:
                recommendations.append(f"Verify FSI compliance as per {rule}")
            elif "SETBACK" in rule:
                recommendations.append(f"Check setback requirements under {rule}")
            elif "HEIGHT" in rule:
                recommendations.append(f"Validate height restrictions per {rule}")

        confidence_score = raw_response.get("confidence_score", 0.75)

        return {
            "project_id": raw_response.get("project_id"),
            "case_id": raw_response.get("case_id"),
            "city": raw_response.get("city"),
            "parameters": raw_response.get("parameters", {}),
            "rules_applied": rules_applied,
            "reasoning": reasoning,
            "confidence_score": confidence_score,
            "confidence_level": raw_response.get("confidence_level", "Medium" if confidence_score > 0.5 else "Low"),
            "violations": violations,
            "recommendations": recommendations,
            "compliant": len(violations) == 0 and confidence_score > 0.5,
            "clause_summaries": clause_summaries,
            "geometry_url": raw_response.get("geometry_url"),
        }

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


class RanjeetRLClient:
    """Client for Ranjeet's RL optimization system (Land Utilization)"""

    def __init__(self):
        self.base_url = settings.RANJEET_RL_URL
        self.api_key = settings.RANJEET_API_KEY
        self.timeout = settings.RANJEET_TIMEOUT
        self.service_available = settings.RANJEET_SERVICE_AVAILABLE

    async def health_check(self) -> ServiceStatus:
        """Check Core-Bucket Data Bridge health"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use the /core/health endpoint from Ranjeet's API
                response = await client.get(f"{self.base_url}/core/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"Core-Bucket bridge health: {health_data.get('status', 'unknown')}")
                    return ServiceStatus.HEALTHY
                else:
                    return ServiceStatus.DEGRADED
        except Exception as e:
            logger.error(f"Core-Bucket bridge health check failed: {e}")
            return ServiceStatus.UNHEALTHY

    async def optimize_design(self, spec_json: Dict, city: str, constraints: Dict = None) -> Dict:
        """Optimize design using Ranjeet's Land Utilization RL System"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {
                "design_spec": spec_json,
                "city": city,
                "constraints": constraints or {},
                "timestamp": datetime.now().isoformat(),
            }

            async with httpx.AsyncClient(timeout=180.0) as client:
                logger.info(f"Calling Ranjeet's RL: {self.base_url}/rl/optimize")
                response = await client.post(f"{self.base_url}/rl/optimize", json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ Ranjeet's RL optimization successful")
                return result

        except Exception as e:
            logger.error(f"Ranjeet's RL optimization failed: {e}")
            raise

    async def submit_feedback(self, feedback_data: Dict) -> Dict:
        """Submit RL feedback for training"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Submitting RL feedback: {self.base_url}/rl/feedback")
                response = await client.post(f"{self.base_url}/rl/feedback", json=feedback_data, headers=headers)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"RL feedback submission error: {e}")
            raise

    async def suggest_iterate(self, spec_json: Dict, strategy: str = "auto_optimize") -> Dict:
        """Get iteration suggestions from RL"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {"spec_json": spec_json, "strategy": strategy}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Getting RL iteration suggestions: {self.base_url}/rl/suggest/iterate")
                response = await client.post(f"{self.base_url}/rl/suggest/iterate", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"RL suggest iterate error: {e}")
            raise


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
