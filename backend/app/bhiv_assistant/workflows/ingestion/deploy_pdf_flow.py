"""
Deploy PDF Ingestion Flow to Prefect
"""

import asyncio
from pathlib import Path

from prefect import serve

from .pdf_to_mcp_flow import PDFIngestionConfig, pdf_ingestion_flow


async def deploy_pdf_flow():
    """Deploy PDF ingestion flow"""

    # Create deployment
    deployment = await pdf_ingestion_flow.to_deployment(
        name="pdf-ingestion-production",
        work_pool_name="default-pool",
        description="Production PDF ingestion workflow",
        tags=["pdf", "ingestion", "mcp", "production"],
        parameters={
            "config": PDFIngestionConfig(
                pdf_source_dir=Path("data/pdfs"), output_dir=Path("data/mcp_rules"), mcp_api_url="http://localhost:8001"
            ).dict()
        },
    )

    print(f"Deployment created: {deployment.name}")
    print(f"Flow ID: {deployment.flow_id}")

    return deployment


if __name__ == "__main__":
    asyncio.run(deploy_pdf_flow())
