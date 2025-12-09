#!/usr/bin/env python3
"""
Deploy Event-Driven Workflows to Prefect
"""

import asyncio

from event_driven_flows import n8n_replacement_flow, scheduled_maintenance_flow, watch_new_files, webhook_triggered_flow


async def deploy_event_driven_workflows():
    """Deploy all event-driven workflows to Prefect"""
    print("Deploying Event-Driven Workflows...")
    print("=" * 50)

    try:
        # Deploy N8N Replacement Flow
        n8n_deployment = await n8n_replacement_flow.to_deployment(
            name="n8n-replacement-flow",
            work_pool_name="default-pool",
            description="Replace n8n workflows: PDF ingestion, log aggregation, geometry verification",
            tags=["n8n-replacement", "pdf", "logs", "geometry"],
        )
        print("✅ N8N Replacement Flow deployed")

        # Deploy File Watcher Flow
        watcher_deployment = await watch_new_files.to_deployment(
            name="file-watcher-flow",
            work_pool_name="default-pool",
            description="Event-driven file processing for PDFs and GLB files",
            tags=["event-driven", "file-watcher", "automation"],
        )
        print("✅ File Watcher Flow deployed")

        # Deploy Scheduled Maintenance Flow
        maintenance_deployment = await scheduled_maintenance_flow.to_deployment(
            name="scheduled-maintenance-flow",
            work_pool_name="default-pool",
            description="Scheduled system maintenance and cleanup",
            tags=["scheduled", "maintenance", "cleanup"],
        )
        print("✅ Scheduled Maintenance Flow deployed")

        # Deploy Webhook Triggered Flow
        webhook_deployment = await webhook_triggered_flow.to_deployment(
            name="webhook-triggered-flow",
            work_pool_name="default-pool",
            description="Flow triggered by external webhooks",
            tags=["webhook", "event-driven", "external-trigger"],
        )
        print("✅ Webhook Triggered Flow deployed")

        print("\n🎉 All event-driven workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 4}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_event_driven_workflows())
    print(f"\nResult: {result}")
