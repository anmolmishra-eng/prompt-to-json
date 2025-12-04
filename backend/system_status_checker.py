"""
Complete System Status Checker
Validates all components are working correctly
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SystemStatusChecker:
    """Check status of all BHIV system components"""

    def __init__(self):
        self.results = {}

    async def check_main_backend(self):
        """Check main FastAPI backend"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8000/api/v1/health")

                if response.status_code == 200:
                    data = response.json()
                    self.results["main_backend"] = {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "data": data,
                    }
                    return True
                else:
                    self.results["main_backend"] = {"status": "unhealthy", "status_code": response.status_code}
                    return False

        except Exception as e:
            self.results["main_backend"] = {"status": "error", "error": str(e)}
            return False

    async def check_bhiv_assistant(self):
        """Check BHIV Assistant service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8003/health")

                if response.status_code == 200:
                    self.results["bhiv_assistant"] = {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                    }
                    return True
                else:
                    self.results["bhiv_assistant"] = {"status": "unhealthy", "status_code": response.status_code}
                    return False

        except Exception as e:
            self.results["bhiv_assistant"] = {"status": "error", "error": str(e)}
            return False

    async def check_prefect_server(self):
        """Check Prefect server"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:4200/api/health")

                if response.status_code == 200:
                    self.results["prefect_server"] = {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                    }
                    return True
                else:
                    self.results["prefect_server"] = {"status": "unhealthy", "status_code": response.status_code}
                    return False

        except Exception as e:
            self.results["prefect_server"] = {"status": "error", "error": str(e)}
            return False

    async def check_mcp_integration(self):
        """Check MCP integration with Sohum's service"""
        try:
            # Check Sohum's service
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get("https://ai-rule-api-w7z5.onrender.com/health")

                if response.status_code == 200:
                    # Check local MCP endpoint
                    local_response = await client.get("http://localhost:8003/mcp/metadata/Mumbai")

                    self.results["mcp_integration"] = {
                        "status": "healthy",
                        "sohum_service": "reachable",
                        "local_endpoint": "working" if local_response.status_code == 200 else "failed",
                    }
                    return True
                else:
                    self.results["mcp_integration"] = {"status": "unhealthy", "sohum_service": "unreachable"}
                    return False

        except Exception as e:
            self.results["mcp_integration"] = {"status": "error", "error": str(e)}
            return False

    async def check_rl_integration(self):
        """Check RL integration"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test RL feedback endpoint
                payload = {"user_id": "system_check", "spec_id": "test_spec", "rating": 4.0, "design_accepted": True}

                response = await client.post("http://localhost:8000/api/v1/rl/feedback", json=payload)

                self.results["rl_integration"] = {
                    "status": "healthy" if response.status_code in [200, 201] else "unhealthy",
                    "status_code": response.status_code,
                }
                return response.status_code in [200, 201]

        except Exception as e:
            self.results["rl_integration"] = {"status": "error", "error": str(e)}
            return False

    def check_storage_system(self):
        """Check storage system"""
        try:
            from app.storage_manager import storage_manager

            validation_results = storage_manager.validate_storage()
            failed_paths = [name for name, success in validation_results.items() if not success]

            self.results["storage_system"] = {
                "status": "healthy" if not failed_paths else "partial",
                "total_paths": len(validation_results),
                "failed_paths": failed_paths,
                "validation_results": validation_results,
            }

            return len(failed_paths) == 0

        except Exception as e:
            self.results["storage_system"] = {"status": "error", "error": str(e)}
            return False

    def check_database_system(self):
        """Check database system"""
        try:
            from app.database_validator import validate_database

            db_healthy = validate_database()

            self.results["database_system"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "validated": db_healthy,
            }

            return db_healthy

        except Exception as e:
            self.results["database_system"] = {"status": "error", "error": str(e)}
            return False

    async def check_workflow_automation(self):
        """Check workflow automation status"""
        try:
            import subprocess

            # Check if workflows are deployed
            result = subprocess.run(
                ["python", "-m", "prefect", "deployment", "ls"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                deployments = (
                    result.stdout.count("pdf-ingestion")
                    + result.stdout.count("log-aggregation")
                    + result.stdout.count("geometry-verification")
                )

                self.results["workflow_automation"] = {
                    "status": "healthy" if deployments >= 3 else "partial",
                    "deployed_workflows": deployments,
                    "expected_workflows": 3,
                }

                return deployments >= 3
            else:
                self.results["workflow_automation"] = {"status": "error", "error": result.stderr}
                return False

        except Exception as e:
            self.results["workflow_automation"] = {"status": "error", "error": str(e)}
            return False

    async def run_complete_check(self):
        """Run complete system status check"""
        logger.info("🔍 BHIV SYSTEM STATUS CHECK")
        logger.info("=" * 50)
        logger.info(f"Started at: {datetime.now()}")
        logger.info("=" * 50)

        checks = [
            ("Storage System", self.check_storage_system),
            ("Database System", self.check_database_system),
            ("Main Backend", self.check_main_backend),
            ("BHIV Assistant", self.check_bhiv_assistant),
            ("Prefect Server", self.check_prefect_server),
            ("MCP Integration", self.check_mcp_integration),
            ("RL Integration", self.check_rl_integration),
            ("Workflow Automation", self.check_workflow_automation),
        ]

        passed_checks = 0
        total_checks = len(checks)

        for check_name, check_func in checks:
            logger.info(f"\n🔍 Checking {check_name}...")

            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                if result:
                    logger.info(f"✅ {check_name}: HEALTHY")
                    passed_checks += 1
                else:
                    logger.warning(f"⚠️ {check_name}: ISSUES DETECTED")

            except Exception as e:
                logger.error(f"❌ {check_name}: CHECK FAILED - {e}")

        # Generate summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 SYSTEM STATUS SUMMARY")
        logger.info("=" * 50)

        for component, status in self.results.items():
            status_icon = {"healthy": "✅", "unhealthy": "⚠️", "partial": "🔶", "error": "❌"}.get(status["status"], "❓")

            logger.info(f"{component:.<30} {status_icon} {status['status'].upper()}")

        overall_health = passed_checks / total_checks
        logger.info(f"\nOverall System Health: {passed_checks}/{total_checks} ({overall_health:.1%})")

        if overall_health >= 0.8:
            logger.info("🎉 System is HEALTHY and ready for production!")
        elif overall_health >= 0.6:
            logger.info("⚠️ System is PARTIALLY HEALTHY - some issues need attention")
        else:
            logger.info("❌ System has CRITICAL ISSUES - immediate attention required")

        # Save detailed results
        results_file = Path("system_status_report.json")
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "overall_health": overall_health,
                    "passed_checks": passed_checks,
                    "total_checks": total_checks,
                    "detailed_results": self.results,
                },
                f,
                indent=2,
            )

        logger.info(f"\n📄 Detailed report saved to: {results_file}")

        return overall_health >= 0.8


async def main():
    """Main status check function"""
    checker = SystemStatusChecker()
    system_healthy = await checker.run_complete_check()

    if not system_healthy:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
