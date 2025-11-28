"""
Work Pool Setup for Custom Infrastructure
Demonstrates custom work pools for running flows on your own infrastructure
"""
import asyncio

from prefect import get_client
from prefect.client.schemas import WorkPool
from prefect.workers.process import ProcessWorkerJobConfiguration


async def setup_custom_work_pools():
    """Setup custom work pools for different environments"""

    async with get_client() as client:
        print("🏗️  Setting up custom work pools...\n")

        # 1. High-performance compliance work pool
        compliance_pool = WorkPool(
            name="compliance-workers",
            type="process",
            description="High-performance workers for compliance processing",
            is_paused=False,
            concurrency_limit=10,
            base_job_template={
                "job_configuration": ProcessWorkerJobConfiguration(
                    command="{{ command }}",
                    env={"PREFECT_LOGGING_LEVEL": "INFO"},
                    working_dir="{{ working_dir }}",
                ).dict(),
                "variables": {
                    "properties": {
                        "command": {
                            "title": "Command",
                            "description": "Command to run",
                            "type": "string",
                            "default": "python -m prefect.engine",
                        }
                    }
                },
            },
        )

        # 2. Development work pool with lower resources
        dev_pool = WorkPool(
            name="dev-workers",
            type="process",
            description="Development workers for testing",
            is_paused=False,
            concurrency_limit=3,
            base_job_template={
                "job_configuration": ProcessWorkerJobConfiguration(
                    command="{{ command }}",
                    env={"PREFECT_LOGGING_LEVEL": "DEBUG"},
                    working_dir="{{ working_dir }}",
                ).dict()
            },
        )

        # 3. GPU work pool for ML tasks
        gpu_pool = WorkPool(
            name="gpu-workers",
            type="process",
            description="GPU workers for ML/AI processing",
            is_paused=False,
            concurrency_limit=2,
            base_job_template={
                "job_configuration": ProcessWorkerJobConfiguration(
                    command="{{ command }}",
                    env={"CUDA_VISIBLE_DEVICES": "0,1", "PREFECT_LOGGING_LEVEL": "INFO"},
                    working_dir="{{ working_dir }}",
                ).dict()
            },
        )

        # Create work pools
        pools = [("compliance-workers", compliance_pool), ("dev-workers", dev_pool), ("gpu-workers", gpu_pool)]

        for pool_name, pool_config in pools:
            try:
                await client.create_work_pool(work_pool=pool_config)
                print(f"✅ Created work pool: {pool_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ️  Work pool already exists: {pool_name}")
                else:
                    print(f"❌ Failed to create {pool_name}: {e}")

        print(f"\n🎯 Work pools setup complete!")
        print("To start workers, run:")
        print("  prefect worker start --pool compliance-workers")
        print("  prefect worker start --pool dev-workers")
        print("  prefect worker start --pool gpu-workers")


def create_worker_start_scripts():
    """Create scripts to start workers easily"""

    # Windows batch script
    windows_script = """@echo off
echo Starting Prefect Workers...

start "Compliance Worker" cmd /k "prefect worker start --pool compliance-workers --name compliance-worker-1"
start "Dev Worker" cmd /k "prefect worker start --pool dev-workers --name dev-worker-1"
start "GPU Worker" cmd /k "prefect worker start --pool gpu-workers --name gpu-worker-1"

echo All workers started!
pause
"""

    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "Starting Prefect Workers..."

# Start workers in background
prefect worker start --pool compliance-workers --name compliance-worker-1 &
prefect worker start --pool dev-workers --name dev-worker-1 &
prefect worker start --pool gpu-workers --name gpu-worker-1 &

echo "All workers started!"
echo "Use 'jobs' to see running workers"
echo "Use 'kill %1 %2 %3' to stop all workers"
"""

    # Write scripts
    with open("start_workers.bat", "w") as f:
        f.write(windows_script)

    with open("start_workers.sh", "w") as f:
        f.write(unix_script)

    print("📝 Worker start scripts created:")
    print("  - start_workers.bat (Windows)")
    print("  - start_workers.sh (Linux/Mac)")


if __name__ == "__main__":
    print("Custom Work Pool Setup")
    print("=" * 30)

    try:
        # Setup work pools
        asyncio.run(setup_custom_work_pools())

        # Create helper scripts
        create_worker_start_scripts()

        print("\n🚀 Next steps:")
        print("1. Start Prefect server: prefect server start")
        print("2. Run workers: ./start_workers.bat (or .sh)")
        print("3. Deploy flows to custom work pools")
        print("4. Monitor execution in Prefect UI")

    except Exception as e:
        print(f"Setup ready (requires Prefect server): {e}")
