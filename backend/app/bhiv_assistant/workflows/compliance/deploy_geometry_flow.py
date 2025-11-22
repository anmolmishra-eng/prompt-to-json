"""
Deploy Geometry Verification Flow to Prefect
"""

import asyncio
from pathlib import Path
from geometry_verification_flow import geometry_verification_flow, GeometryConfig


async def deploy_geometry_verification_flow():
    """Deploy geometry verification flow"""
    
    # Create deployment
    deployment = await geometry_verification_flow.to_deployment(
        name="geometry-verification-daily",
        work_pool_name="default-pool",
        description="Daily geometry verification for GLB outputs",
        tags=["geometry", "verification", "quality", "glb", "compliance"],
        parameters={
            "config": GeometryConfig(
                glb_source_dir=Path("data/geometry_outputs"),
                output_dir=Path("reports/geometry_verification"),
                max_file_size_mb=50.0
            ).dict()
        }
    )
    
    print(f"Deployment created: {deployment.name}")
    print(f"Description: {deployment.description}")
    print(f"Flow ID: {deployment.flow_id}")
    
    return deployment


if __name__ == "__main__":
    asyncio.run(deploy_geometry_verification_flow())