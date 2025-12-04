"""
Activate BHIV Automation - Start all automated processes
This script activates all automation components and ensures they're running
"""

import asyncio
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AutomationActivator:
    """Activate and manage all BHIV automation components"""

    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent

    async def check_service_health(self, url: str, name: str, timeout: int = 10) -> bool:
        """Check if a service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    logger.info(f"✅ {name} is healthy")
                    return True
                else:
                    logger.warning(f"⚠️ {name} returned status {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ {name} health check failed: {e}")
            return False

    def start_prefect_server(self):
        """Start Prefect server"""
        try:
            logger.info("🚀 Starting Prefect server...")
            process = subprocess.Popen(
                [sys.executable, "-m", "prefect", "server", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            self.processes["prefect_server"] = process
            logger.info("✅ Prefect server started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Prefect server: {e}")
            return False

    def start_prefect_worker(self):
        """Start Prefect worker"""
        try:
            logger.info("🚀 Starting Prefect worker...")
            process = subprocess.Popen(
                [sys.executable, "-m", "prefect", "worker", "start", "--pool", "default-pool"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes["prefect_worker"] = process
            logger.info("✅ Prefect worker started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Prefect worker: {e}")
            return False

    async def deploy_workflows(self):
        """Deploy all Prefect workflows"""
        try:
            logger.info("📦 Deploying workflows...")

            # Import and run deployment
            sys.path.append(str(self.base_dir / "app" / "bhiv_assistant"))
            from workflows.deploy_all_flows import deploy_all_workflows

            result = await deploy_all_workflows()

            if result["status"] == "success":
                logger.info("✅ All workflows deployed successfully")
                return True
            else:
                logger.error(f"❌ Workflow deployment failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to deploy workflows: {e}")
            return False

    async def trigger_initial_workflows(self):
        """Trigger initial workflow runs"""
        try:
            logger.info("🎯 Triggering initial workflow runs...")

            workflows = ["pdf-ingestion-daily", "log-aggregation-hourly", "geometry-verification-6h"]

            for workflow in workflows:
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "prefect", "deployment", "run", workflow],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        logger.info(f"✅ Triggered {workflow}")
                    else:
                        logger.warning(f"⚠️ Failed to trigger {workflow}: {result.stderr}")

                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Timeout triggering {workflow}")
                except Exception as e:
                    logger.error(f"❌ Error triggering {workflow}: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to trigger workflows: {e}")
            return False

    def setup_scheduled_tasks(self):
        """Set up scheduled tasks for automation"""
        try:
            logger.info("⏰ Setting up scheduled tasks...")

            # Create a simple scheduler script
            scheduler_script = self.base_dir / "automation_scheduler.py"

            scheduler_code = '''
import schedule
import time
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pdf_ingestion():
    """Run PDF ingestion workflow"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "prefect", "deployment", "run", "pdf-ingestion-daily"
        ], capture_output=True, text=True)
        logger.info(f"PDF ingestion result: {result.returncode}")
    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")

def run_log_aggregation():
    """Run log aggregation workflow"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "prefect", "deployment", "run", "log-aggregation-hourly"
        ], capture_output=True, text=True)
        logger.info(f"Log aggregation result: {result.returncode}")
    except Exception as e:
        logger.error(f"Log aggregation failed: {e}")

def run_geometry_verification():
    """Run geometry verification workflow"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "prefect", "deployment", "run", "geometry-verification-6h"
        ], capture_output=True, text=True)
        logger.info(f"Geometry verification result: {result.returncode}")
    except Exception as e:
        logger.error(f"Geometry verification failed: {e}")

# Schedule tasks
schedule.every().day.at("02:00").do(run_pdf_ingestion)
schedule.every().hour.do(run_log_aggregation)
schedule.every(6).hours.do(run_geometry_verification)

logger.info("Scheduler started - automation is active")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
'''

            with open(scheduler_script, "w") as f:
                f.write(scheduler_code)

            logger.info(f"✅ Scheduler script created: {scheduler_script}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to setup scheduled tasks: {e}")
            return False

    def start_scheduler(self):
        """Start the automation scheduler"""
        try:
            scheduler_script = self.base_dir / "automation_scheduler.py"

            if not scheduler_script.exists():
                logger.error("❌ Scheduler script not found")
                return False

            logger.info("🚀 Starting automation scheduler...")
            process = subprocess.Popen(
                [sys.executable, str(scheduler_script)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            self.processes["scheduler"] = process
            logger.info("✅ Automation scheduler started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            return False

    async def activate_full_automation(self):
        """Activate complete automation system"""
        logger.info("🎯 ACTIVATING BHIV AUTOMATION SYSTEM")
        logger.info("=" * 50)

        steps = [
            ("Installing dependencies", self.install_dependencies),
            ("Starting Prefect server", self.start_prefect_server),
            ("Waiting for Prefect server", lambda: self.wait_for_service("http://localhost:4200", "Prefect")),
            ("Deploying workflows", self.deploy_workflows),
            ("Starting Prefect worker", self.start_prefect_worker),
            ("Setting up scheduled tasks", self.setup_scheduled_tasks),
            ("Triggering initial workflows", self.trigger_initial_workflows),
            ("Starting automation scheduler", self.start_scheduler),
        ]

        results = {}

        for step_name, step_func in steps:
            logger.info(f"\n🔄 {step_name}...")
            try:
                if asyncio.iscoroutinefunction(step_func):
                    result = await step_func()
                else:
                    result = step_func()
                results[step_name] = result

                if result:
                    logger.info(f"✅ {step_name} completed")
                else:
                    logger.error(f"❌ {step_name} failed")

            except Exception as e:
                logger.error(f"❌ {step_name} crashed: {e}")
                results[step_name] = False

        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 AUTOMATION ACTIVATION SUMMARY")
        logger.info("=" * 50)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        for step, result in results.items():
            status = "✅ SUCCESS" if result else "❌ FAILED"
            logger.info(f"{step:.<40} {status}")

        logger.info(f"\nOverall: {passed}/{total} steps completed")

        if passed == total:
            logger.info("🎉 AUTOMATION FULLY ACTIVATED!")
            logger.info("\n📋 Active Components:")
            logger.info("  • Prefect Server: http://localhost:4200")
            logger.info("  • Prefect Worker: Running")
            logger.info("  • PDF Ingestion: Daily at 2:00 AM")
            logger.info("  • Log Aggregation: Every hour")
            logger.info("  • Geometry Verification: Every 6 hours")
            logger.info("  • Automation Scheduler: Running")
        else:
            logger.warning("⚠️ Partial automation activation - check failed steps")

        return passed == total

    def install_dependencies(self):
        """Install required dependencies"""
        try:
            logger.info("📦 Installing automation dependencies...")

            dependencies = ["prefect>=2.14.0", "schedule>=1.2.0"]

            for dep in dependencies:
                result = subprocess.run([sys.executable, "-m", "pip", "install", dep], capture_output=True, text=True)

                if result.returncode != 0:
                    logger.warning(f"⚠️ Failed to install {dep}: {result.stderr}")

            logger.info("✅ Dependencies installation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False

    async def wait_for_service(self, url: str, name: str, max_wait: int = 60):
        """Wait for service to become available"""
        logger.info(f"⏳ Waiting for {name} to be ready...")

        for i in range(max_wait):
            if await self.check_service_health(url, name, timeout=5):
                return True
            await asyncio.sleep(1)

        logger.error(f"❌ {name} did not become ready within {max_wait} seconds")
        return False

    def stop_all_processes(self):
        """Stop all started processes"""
        logger.info("🛑 Stopping all automation processes...")

        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ Stopped {name}")
            except Exception as e:
                logger.error(f"❌ Failed to stop {name}: {e}")
                try:
                    process.kill()
                except:
                    pass


async def main():
    """Main activation function"""
    activator = AutomationActivator()

    try:
        success = await activator.activate_full_automation()

        if success:
            logger.info("\n🎉 BHIV Automation is now ACTIVE!")
            logger.info("Press Ctrl+C to stop all processes")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(10)
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down automation...")
                activator.stop_all_processes()
        else:
            logger.error("\n❌ Automation activation failed")
            activator.stop_all_processes()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Activation interrupted")
        activator.stop_all_processes()
    except Exception as e:
        logger.error(f"\n💥 Activation crashed: {e}")
        activator.stop_all_processes()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
