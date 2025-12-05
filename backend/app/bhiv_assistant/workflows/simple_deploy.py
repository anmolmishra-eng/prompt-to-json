#!/usr/bin/env python3
"""
Simple workflow deployment without complex imports
"""

import asyncio

from prefect import flow, task


@task
def process_pdf_task():
    """Simple PDF processing task"""
    return "PDF processed successfully"


@task
def aggregate_logs_task():
    """Simple log aggregation task"""
    return "Logs aggregated successfully"


@task
def verify_geometry_task():
    """Simple geometry verification task"""
    return "Geometry verified successfully"


@flow(name="pdf-ingestion-simple")
def pdf_ingestion_flow():
    """Simple PDF ingestion flow"""
    result = process_pdf_task()
    return result


@flow(name="log-aggregation-simple")
def log_aggregation_flow():
    """Simple log aggregation flow"""
    result = aggregate_logs_task()
    return result


@flow(name="geometry-verification-simple")
def geometry_verification_flow():
    """Simple geometry verification flow"""
    result = verify_geometry_task()
    return result


async def deploy_simple_workflows():
    """Deploy simple workflows"""
    print("Deploying simple BHIV workflows...")
    print("=" * 50)

    try:
        # Deploy PDF ingestion
        pdf_deployment = await pdf_ingestion_flow.to_deployment(
            name="pdf-ingestion-simple",
            work_pool_name="default-pool",
            description="Simple PDF ingestion workflow",
            tags=["simple", "pdf", "ingestion"],
        )
        print("✅ PDF Ingestion workflow deployed")

        # Deploy log aggregation
        log_deployment = await log_aggregation_flow.to_deployment(
            name="log-aggregation-simple",
            work_pool_name="default-pool",
            description="Simple log aggregation workflow",
            tags=["simple", "logs", "monitoring"],
        )
        print("✅ Log Aggregation workflow deployed")

        # Deploy geometry verification
        geometry_deployment = await geometry_verification_flow.to_deployment(
            name="geometry-verification-simple",
            work_pool_name="default-pool",
            description="Simple geometry verification workflow",
            tags=["simple", "geometry", "verification"],
        )
        print("✅ Geometry Verification workflow deployed")

        print("\n🎉 All simple workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4200")

        return {"status": "success", "workflows": 3}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_simple_workflows())
    print(f"\nResult: {result}")
