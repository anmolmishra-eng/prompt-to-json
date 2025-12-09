#!/usr/bin/env python3
"""
Deploy MCP Compliance Workflows to Prefect
"""

import asyncio

from mcp_compliance_flow import geometry_verification_flow, log_aggregation_flow, mcp_compliance_flow


async def deploy_mcp_workflows():
    """Deploy all MCP workflows to Prefect"""
    print("Deploying MCP Compliance Workflows...")
    print("=" * 50)

    try:
        # Deploy MCP Compliance Flow
        mcp_deployment = await mcp_compliance_flow.to_deployment(
            name="mcp-compliance-workflow",
            work_pool_name="default-pool",
            description="PDF ingestion and MCP compliance processing",
            tags=["mcp", "compliance", "pdf", "workflow"],
        )
        print("✅ MCP Compliance Workflow deployed")

        # Deploy Log Aggregation Flow
        log_deployment = await log_aggregation_flow.to_deployment(
            name="log-aggregation-workflow",
            work_pool_name="default-pool",
            description="Aggregate logs from multiple workflow runs",
            tags=["logs", "aggregation", "monitoring"],
        )
        print("✅ Log Aggregation Workflow deployed")

        # Deploy Geometry Verification Flow
        geometry_deployment = await geometry_verification_flow.to_deployment(
            name="geometry-verification-workflow",
            work_pool_name="default-pool",
            description="Verify .glb geometry files",
            tags=["geometry", "verification", "validation"],
        )
        print("✅ Geometry Verification Workflow deployed")

        print("\n🎉 All MCP workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 3}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_mcp_workflows())
    print(f"\nResult: {result}")
