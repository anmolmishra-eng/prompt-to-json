#!/usr/bin/env python3
"""
Deploy Notification and Monitoring Workflows to Prefect
"""

import asyncio

from notification_flows import (
    monitored_mcp_flow,
    monitored_rl_flow,
    reliable_workflow_with_retries,
    system_health_monitoring_flow,
)


async def deploy_notification_workflows():
    """Deploy all notification and monitoring workflows to Prefect"""
    print("Deploying Notification & Monitoring Workflows...")
    print("=" * 50)

    try:
        # Deploy Monitored RL Flow
        rl_deployment = await monitored_rl_flow.to_deployment(
            name="monitored-rl-flow",
            work_pool_name="default-pool",
            description="RL optimization with Slack/email notifications",
            tags=["rl", "monitoring", "notifications", "alerts"],
        )
        print("✅ Monitored RL Flow deployed")

        # Deploy Monitored MCP Flow
        mcp_deployment = await monitored_mcp_flow.to_deployment(
            name="monitored-mcp-flow",
            work_pool_name="default-pool",
            description="MCP compliance with Slack/email notifications",
            tags=["mcp", "monitoring", "notifications", "alerts"],
        )
        print("✅ Monitored MCP Flow deployed")

        # Deploy System Health Monitoring
        health_deployment = await system_health_monitoring_flow.to_deployment(
            name="system-health-monitoring",
            work_pool_name="default-pool",
            description="System health monitoring with alerts",
            tags=["health", "monitoring", "system", "alerts"],
        )
        print("✅ System Health Monitoring deployed")

        # Deploy Reliable Workflow with Retries
        reliable_deployment = await reliable_workflow_with_retries.to_deployment(
            name="reliable-workflow-retries",
            work_pool_name="default-pool",
            description="Reliable workflow execution with retries and notifications",
            tags=["reliability", "retries", "notifications", "robust"],
        )
        print("✅ Reliable Workflow with Retries deployed")

        print("\n🎉 All notification workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 4}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_notification_workflows())
    print(f"\nResult: {result}")
