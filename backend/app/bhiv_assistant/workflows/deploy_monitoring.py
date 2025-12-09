#!/usr/bin/env python3
"""
Deploy Monitoring Workflows to Prefect
"""

import asyncio

from monitoring_flows import mcp_flow_with_alerts, rl_flow_with_alerts, system_monitoring_flow


async def deploy_monitoring_workflows():
    """Deploy all monitoring workflows to Prefect"""
    print("Deploying Monitoring Workflows...")
    print("=" * 50)

    try:
        # Deploy MCP Workflow with Alerts
        mcp_deployment = await mcp_flow_with_alerts.to_deployment(
            name="mcp-workflow-with-alerts",
            work_pool_name="default-pool",
            description="MCP compliance workflow with error handling and alerts",
            tags=["mcp", "monitoring", "alerts", "error-handling"],
        )
        print("✅ MCP Workflow with Alerts deployed")

        # Deploy RL Workflow with Alerts
        rl_deployment = await rl_flow_with_alerts.to_deployment(
            name="rl-workflow-with-alerts",
            work_pool_name="default-pool",
            description="Multi-city RL workflow with error handling and alerts",
            tags=["rl", "monitoring", "alerts", "error-handling"],
        )
        print("✅ RL Workflow with Alerts deployed")

        # Deploy System Monitoring Workflow
        monitoring_deployment = await system_monitoring_flow.to_deployment(
            name="system-monitoring-workflow",
            work_pool_name="default-pool",
            description="Generate system monitoring reports and alerts",
            tags=["monitoring", "reports", "system-health"],
        )
        print("✅ System Monitoring Workflow deployed")

        print("\n🎉 All monitoring workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 3}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_monitoring_workflows())
    print(f"\nResult: {result}")
