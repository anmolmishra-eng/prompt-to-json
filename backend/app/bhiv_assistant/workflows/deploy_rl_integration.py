#!/usr/bin/env python3
"""
Deploy RL Integration Workflows to Prefect
"""

import asyncio

from rl_integration_flows import rl_optimization_flow, rl_training_flow


async def deploy_rl_integration_workflows():
    """Deploy RL integration workflows to Prefect"""
    print("Deploying RL Integration Workflows...")
    print("=" * 50)

    try:
        # Deploy RL Optimization Flow
        optimization_deployment = await rl_optimization_flow.to_deployment(
            name="rl-optimization-flow",
            work_pool_name="default-pool",
            description="RL optimization using existing PPO model",
            tags=["rl", "optimization", "ppo", "existing-model"],
        )
        print("✅ RL Optimization Flow deployed")

        # Deploy RL Training Flow
        training_deployment = await rl_training_flow.to_deployment(
            name="rl-training-flow",
            work_pool_name="default-pool",
            description="Train RL model based on user feedback",
            tags=["rl", "training", "feedback", "ppo"],
        )
        print("✅ RL Training Flow deployed")

        print("\n🎉 All RL integration workflows deployed successfully!")
        print("Access Prefect UI: http://localhost:4201")

        return {"status": "success", "workflows": 2}

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(deploy_rl_integration_workflows())
    print(f"\nResult: {result}")
