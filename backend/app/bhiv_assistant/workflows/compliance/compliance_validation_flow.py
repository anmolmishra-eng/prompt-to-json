"""
Compliance Validation Workflow
Validates design outputs against building codes and regulations
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List

import httpx
from prefect import flow, task
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ComplianceConfig(BaseModel):
    """Configuration for compliance validation"""

    bhiv_api_url: str = "http://localhost:8003"
    output_dir: Path = Path("reports/compliance")
    cities: List[str] = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]


@task(name="fetch-recent-designs")
async def fetch_recent_designs(api_url: str) -> List[Dict]:
    """Fetch recent designs from BHIV API for validation"""
    url = f"{api_url}/bhiv/v1/designs/recent"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            designs = response.json()
            logger.info(f"Fetched {len(designs)} recent designs for validation")
            return designs

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch recent designs: {e}")
            return []


@task(name="validate-design-compliance")
async def validate_design_compliance(design: Dict, api_url: str) -> Dict:
    """Validate a single design against compliance rules"""
    url = f"{api_url}/api/v1/compliance/check"

    payload = {
        "design_id": design.get("design_id"),
        "city": design.get("city", "Mumbai"),
        "regulations": ["IBC", "ADA", "Local"],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()

            compliance_result = response.json()

            return {
                "design_id": design.get("design_id"),
                "city": design.get("city"),
                "compliant": compliance_result.get("compliant", False),
                "violations": compliance_result.get("violations", []),
                "score": compliance_result.get("score", 0),
                "status": "validated",
            }

        except httpx.HTTPError as e:
            logger.error(f"Compliance validation failed for design {design.get('design_id')}: {e}")
            return {
                "design_id": design.get("design_id"),
                "city": design.get("city"),
                "status": "error",
                "error": str(e),
            }


@task(name="generate-compliance-report")
def generate_compliance_report(validation_results: List[Dict], output_dir: Path) -> Path:
    """Generate compliance validation report"""
    import json
    from datetime import datetime

    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    compliant = [r for r in validation_results if r.get("compliant") == True]
    non_compliant = [r for r in validation_results if r.get("compliant") == False]
    errors = [r for r in validation_results if r.get("status") == "error"]

    # Calculate compliance rate by city
    city_stats = {}
    for result in validation_results:
        city = result.get("city", "Unknown")
        if city not in city_stats:
            city_stats[city] = {"total": 0, "compliant": 0}

        city_stats[city]["total"] += 1
        if result.get("compliant"):
            city_stats[city]["compliant"] += 1

    # Add compliance rates
    for city, stats in city_stats.items():
        stats["compliance_rate"] = f"{(stats['compliant'] / stats['total'] * 100):.1f}%" if stats["total"] > 0 else "0%"

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_designs": len(validation_results),
            "compliant": len(compliant),
            "non_compliant": len(non_compliant),
            "errors": len(errors),
            "overall_compliance_rate": f"{(len(compliant) / len(validation_results) * 100):.1f}%"
            if validation_results
            else "0%",
        },
        "city_breakdown": city_stats,
        "validation_results": validation_results,
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Compliance report saved to {report_file}")
    logger.info(f"Overall compliance rate: {report['summary']['overall_compliance_rate']}")

    return report_file


@flow(
    name="compliance-validation",
    description="Validate design outputs against building codes and regulations",
    version="1.0",
)
async def compliance_validation_flow(config: ComplianceConfig = ComplianceConfig()):
    """
    Main flow: Fetch designs → Validate compliance → Generate report
    """
    logger.info("Starting compliance validation flow...")

    # Step 1: Fetch recent designs
    designs = await fetch_recent_designs(config.bhiv_api_url)

    if not designs:
        logger.info("No recent designs found for validation")
        return {"status": "no_designs", "validated": 0}

    # Step 2: Validate each design
    validation_tasks = [validate_design_compliance(design, config.bhiv_api_url) for design in designs]

    validation_results = await asyncio.gather(*validation_tasks)

    # Step 3: Generate report
    report_file = generate_compliance_report(validation_results, config.output_dir)

    logger.info("Compliance validation flow complete")

    return {"status": "complete", "total_designs": len(validation_results), "report_file": str(report_file)}


if __name__ == "__main__":
    asyncio.run(compliance_validation_flow())
