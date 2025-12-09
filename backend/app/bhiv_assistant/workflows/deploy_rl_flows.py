#!/usr/bin/env python3
"""
Deploy Multi-City RL Workflows to Prefect
"""

import asyncio

from multi_city_rl_flow import multi_city_rl_flow, rl_feedback_loop_flow


async def deploy_rl_workflows():
    """Deploy all RL workflows to Prefect"""
    print("Deploying Multi-City RL Workflows...")
    print("=" * 50)

    try:
        # Deploy Multi-City RL Flow
        rl_deployment = await multi_city_rl_flow.to_deployment(
            name="multi-city-rl-workflow",
            work_pool_name="default-pool",
            description="Multi-city RL optimization for Mumbai, Pune, Nashik, Ahmedabad",
            tags=["rl", "multi-city", "optimization", "land-use"],
        )
        print("✅ Multi-City RL Workflow deployed")

        # Deploy RL Feedback Loop Flow
        feedback_deployment = await rl_feedback_loop_flow.to_deployment(
            name="rl-feedback-loop-workflow",
            work_pool_name="default-pool",
            description="Process user feedback and update RL model weights",
            tags=["rl", "feedback", "learning", "model-update"],
        )
        print("✅ RL Feedback Loop Workflow deployed")

        print("\n🎉 All RL workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 2}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_rl_workflows())
    print(f"\nResult: {result}")
