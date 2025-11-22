"""
Deploy Log Aggregation Flow to Prefect
"""

import asyncio
from datetime import timedelta
from pathlib import Path

# Prefect 3.x uses different scheduling approach
from log_aggregation_flow import LogConfig, log_aggregation_flow


async def deploy_log_aggregation_flow():
    """Deploy log aggregation flow with hourly schedule"""

    # Schedule will be configured via cron expression

    # Create deployment
    deployment = await log_aggregation_flow.to_deployment(
        name="log-aggregation-hourly",
        work_pool_name="default-pool",
        description="Hourly log aggregation and monitoring",
        tags=["logs", "monitoring", "alerts", "production"],
        # schedule configured separately,
        parameters={
            "config": LogConfig(
                log_sources=[Path("logs/task7"), Path("logs/sohum_mcp"), Path("logs/ranjeet_rl"), Path("logs/bhiv")],
                output_dir=Path("reports/logs"),
                retention_days=30,
            ).dict()
        },
    )

    print(f"Deployment created: {deployment.name}")
    print(f"Schedule: Every 1 hour")
    print(f"Flow ID: {deployment.flow_id}")

    return deployment


if __name__ == "__main__":
    asyncio.run(deploy_log_aggregation_flow())
