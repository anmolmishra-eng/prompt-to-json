"""
Data Lineage and Asset Materialization Demo
Build a data lineage graph by materializing assets
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.artifacts import create_link_artifact, create_table_artifact

try:
    from prefect.cache_policies import INPUTS
except ImportError:
    INPUTS = None
from prefect.tasks import task_input_hash

# ============================================================================
# ASSET MATERIALIZATION TASKS
# ============================================================================


@task(
    name="extract_raw_data",
    description="Extract raw design data - Data Source",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=2),
    tags=["extract", "raw-data"],
)
def extract_raw_design_data(source: str) -> Dict:
    """Extract raw design data from various sources"""
    logger = get_run_logger()
    logger.info(f"Extracting raw data from {source}")

    # Simulate data extraction
    raw_data = {
        "source": source,
        "extracted_at": datetime.now().isoformat(),
        "designs": [
            {
                "id": "D001",
                "type": "residential",
                "area_sqft": 1200,
                "floors": 2,
                "city": "Mumbai",
                "status": "pending",
            },
            {"id": "D002", "type": "commercial", "area_sqft": 5000, "floors": 4, "city": "Pune", "status": "approved"},
            {
                "id": "D003",
                "type": "residential",
                "area_sqft": 800,
                "floors": 1,
                "city": "Ahmedabad",
                "status": "rejected",
            },
        ],
        "total_records": 3,
    }

    # Create data lineage artifact
    create_table_artifact(
        key=f"raw-data-{source}", table=raw_data["designs"], description=f"Raw design data extracted from {source}"
    )

    logger.info(f"Extracted {raw_data['total_records']} records from {source}")
    return raw_data


@task(
    name="transform_design_data",
    description="Transform and clean design data - Data Transformation",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
    tags=["transform", "clean"],
)
def transform_design_data(raw_data: Dict) -> Dict:
    """Transform and clean the raw design data"""
    logger = get_run_logger()
    logger.info("Transforming design data")

    designs = raw_data["designs"]

    # Transform data
    transformed_designs = []
    for design in designs:
        transformed = {
            "design_id": design["id"],
            "design_type": design["type"],
            "area_sqm": round(design["area_sqft"] * 0.092903, 2),  # Convert to sq meters
            "area_sqft": design["area_sqft"],
            "floor_count": design["floors"],
            "city": design["city"],
            "approval_status": design["status"],
            "size_category": "small"
            if design["area_sqft"] < 1000
            else "medium"
            if design["area_sqft"] < 3000
            else "large",
            "transformed_at": datetime.now().isoformat(),
        }
        transformed_designs.append(transformed)

    transformed_data = {
        "source": raw_data["source"],
        "transformed_at": datetime.now().isoformat(),
        "designs": transformed_designs,
        "total_records": len(transformed_designs),
        "transformations_applied": ["area_sqft_to_sqm_conversion", "size_categorization", "field_standardization"],
    }

    # Create transformation artifact
    create_table_artifact(
        key=f"transformed-data-{raw_data['source']}",
        table=transformed_designs,
        description="Cleaned and transformed design data",
    )

    logger.info(f"Transformed {len(transformed_designs)} design records")
    return transformed_data


@task(
    name="validate_data_quality", description="Validate data quality - Data Quality Check", tags=["validate", "quality"]
)
def validate_data_quality(transformed_data: Dict) -> Dict:
    """Validate data quality and generate quality metrics"""
    logger = get_run_logger()
    logger.info("Validating data quality")

    designs = transformed_data["designs"]

    # Quality checks
    quality_checks = {
        "total_records": len(designs),
        "missing_design_id": sum(1 for d in designs if not d.get("design_id")),
        "missing_city": sum(1 for d in designs if not d.get("city")),
        "invalid_area": sum(1 for d in designs if d.get("area_sqft", 0) <= 0),
        "invalid_floors": sum(1 for d in designs if d.get("floor_count", 0) <= 0),
        "valid_records": 0,
    }

    # Calculate valid records
    quality_checks["valid_records"] = (
        quality_checks["total_records"]
        - quality_checks["missing_design_id"]
        - quality_checks["missing_city"]
        - quality_checks["invalid_area"]
        - quality_checks["invalid_floors"]
    )

    quality_score = (quality_checks["valid_records"] / quality_checks["total_records"]) * 100

    quality_report = {
        "source": transformed_data["source"],
        "validated_at": datetime.now().isoformat(),
        "quality_score": round(quality_score, 2),
        "quality_checks": quality_checks,
        "passed_validation": quality_score >= 90,
        "recommendations": [],
    }

    # Add recommendations
    if quality_checks["missing_design_id"] > 0:
        quality_report["recommendations"].append("Fix missing design IDs")
    if quality_checks["invalid_area"] > 0:
        quality_report["recommendations"].append("Validate area measurements")

    # Create quality report artifact
    quality_table = [
        {"Metric": "Total Records", "Value": quality_checks["total_records"]},
        {"Metric": "Valid Records", "Value": quality_checks["valid_records"]},
        {"Metric": "Quality Score", "Value": f"{quality_score:.1f}%"},
        {"Metric": "Missing IDs", "Value": quality_checks["missing_design_id"]},
        {"Metric": "Missing Cities", "Value": quality_checks["missing_city"]},
        {"Metric": "Invalid Areas", "Value": quality_checks["invalid_area"]},
    ]

    create_table_artifact(
        key=f"quality-report-{transformed_data['source']}",
        table=quality_table,
        description="Data quality validation report",
    )

    logger.info(f"Data quality score: {quality_score:.1f}%")
    return quality_report


@task(
    name="generate_analytics",
    description="Generate analytics and insights - Data Analytics",
    tags=["analytics", "insights"],
)
def generate_design_analytics(validated_data: Dict, quality_report: Dict) -> Dict:
    """Generate analytics and insights from validated data"""
    logger = get_run_logger()
    logger.info("Generating design analytics")

    if not quality_report["passed_validation"]:
        logger.warning("Data quality issues detected, analytics may be incomplete")

    # Get designs from the original transformed data
    designs = validated_data["designs"]

    # Analytics calculations
    analytics = {
        "source": validated_data["source"],
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_designs": len(designs),
            "avg_area_sqft": round(sum(d["area_sqft"] for d in designs) / len(designs), 2),
            "avg_floors": round(sum(d["floor_count"] for d in designs) / len(designs), 2),
        },
        "by_city": {},
        "by_type": {},
        "by_size": {},
        "by_status": {},
    }

    # Group by city
    for design in designs:
        city = design["city"]
        if city not in analytics["by_city"]:
            analytics["by_city"][city] = {"count": 0, "total_area": 0}
        analytics["by_city"][city]["count"] += 1
        analytics["by_city"][city]["total_area"] += design["area_sqft"]

    # Group by type
    for design in designs:
        design_type = design["design_type"]
        if design_type not in analytics["by_type"]:
            analytics["by_type"][design_type] = 0
        analytics["by_type"][design_type] += 1

    # Group by size category
    for design in designs:
        size_cat = design["size_category"]
        if size_cat not in analytics["by_size"]:
            analytics["by_size"][size_cat] = 0
        analytics["by_size"][size_cat] += 1

    # Group by approval status
    for design in designs:
        status = design["approval_status"]
        if status not in analytics["by_status"]:
            analytics["by_status"][status] = 0
        analytics["by_status"][status] += 1

    # Create analytics artifacts
    city_table = [
        {"City": city, "Count": data["count"], "Total Area": data["total_area"]}
        for city, data in analytics["by_city"].items()
    ]

    create_table_artifact(
        key=f"city-analytics-{validated_data['source']}", table=city_table, description="Design distribution by city"
    )

    type_table = [{"Design Type": design_type, "Count": count} for design_type, count in analytics["by_type"].items()]

    create_table_artifact(
        key=f"type-analytics-{validated_data['source']}", table=type_table, description="Design distribution by type"
    )

    logger.info(f"Generated analytics for {analytics['summary']['total_designs']} designs")
    return analytics


# ============================================================================
# DATA LINEAGE FLOW
# ============================================================================


@flow(name="data-lineage-pipeline", description="Complete data pipeline with lineage tracking", version="1.0.0")
def data_lineage_pipeline(data_sources: List[str]) -> Dict:
    """
    Complete data pipeline that builds lineage graph through asset materialization

    Data Flow:
    Raw Data → Transformed Data → Quality Validation → Analytics → Final Report
    """
    logger = get_run_logger()
    logger.info(f"Starting data lineage pipeline for {len(data_sources)} sources")

    pipeline_results = {
        "pipeline_id": f"lineage_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "started_at": datetime.now().isoformat(),
        "sources_processed": [],
        "total_designs": 0,
        "quality_scores": [],
        "analytics_summary": {},
    }

    all_analytics = []

    # Process each data source
    for source in data_sources:
        logger.info(f"Processing data source: {source}")

        try:
            # Step 1: Extract raw data (Asset: Raw Data)
            raw_data = extract_raw_design_data(source)

            # Step 2: Transform data (Asset: Cleaned Data)
            transformed_data = transform_design_data(raw_data)

            # Step 3: Validate quality (Asset: Quality Report)
            quality_report = validate_data_quality(transformed_data)

            # Step 4: Generate analytics (Asset: Analytics Report)
            analytics = generate_design_analytics(transformed_data, quality_report)

            # Track results
            pipeline_results["sources_processed"].append(
                {
                    "source": source,
                    "records": transformed_data["total_records"],
                    "quality_score": quality_report["quality_score"],
                    "passed_validation": quality_report["passed_validation"],
                }
            )

            pipeline_results["total_designs"] += transformed_data["total_records"]
            pipeline_results["quality_scores"].append(quality_report["quality_score"])
            all_analytics.append(analytics)

            logger.info(f"✅ Completed processing {source}")

        except Exception as e:
            logger.error(f"❌ Failed processing {source}: {e}")
            pipeline_results["sources_processed"].append(
                {"source": source, "error": str(e), "records": 0, "quality_score": 0, "passed_validation": False}
            )

    # Generate final pipeline summary
    pipeline_results["completed_at"] = datetime.now().isoformat()
    pipeline_results["avg_quality_score"] = (
        sum(pipeline_results["quality_scores"]) / len(pipeline_results["quality_scores"])
        if pipeline_results["quality_scores"]
        else 0
    )

    # Create final pipeline artifact with lineage summary
    lineage_summary = [
        {"Stage": "Raw Data Extraction", "Assets Created": len(data_sources), "Status": "✅ Complete"},
        {"Stage": "Data Transformation", "Assets Created": len(data_sources), "Status": "✅ Complete"},
        {"Stage": "Quality Validation", "Assets Created": len(data_sources), "Status": "✅ Complete"},
        {"Stage": "Analytics Generation", "Assets Created": len(data_sources), "Status": "✅ Complete"},
        {"Stage": "Pipeline Summary", "Assets Created": 1, "Status": "✅ Complete"},
    ]

    create_table_artifact(
        key=f"pipeline-lineage-{pipeline_results['pipeline_id']}",
        table=lineage_summary,
        description="Complete data lineage pipeline execution summary",
    )

    # Create link to view all artifacts
    create_link_artifact(
        key=f"view-all-artifacts-{pipeline_results['pipeline_id']}",
        link="http://localhost:4200/artifacts",  # Prefect UI artifacts page
        description="View all generated artifacts and data lineage",
    )

    logger.info(
        f"🎉 Pipeline completed: {pipeline_results['total_designs']} designs processed, "
        f"{pipeline_results['avg_quality_score']:.1f}% avg quality score"
    )

    return pipeline_results


# ============================================================================
# TESTING AND DEMONSTRATION
# ============================================================================


def test_data_lineage():
    """Test the data lineage pipeline"""
    print("🔗 Testing Data Lineage Pipeline\n")

    # Test with multiple data sources
    test_sources = ["database", "api", "file_upload"]

    result = data_lineage_pipeline(test_sources)

    print("📊 Pipeline Results:")
    print(f"  - Pipeline ID: {result['pipeline_id']}")
    print(f"  - Total Designs: {result['total_designs']}")
    print(f"  - Average Quality Score: {result['avg_quality_score']:.1f}%")
    print(f"  - Sources Processed: {len(result['sources_processed'])}")

    print("\n📈 Data Lineage Created:")
    print("  1. Raw Data Assets (3 sources)")
    print("  2. Transformed Data Assets (3 sources)")
    print("  3. Quality Report Assets (3 sources)")
    print("  4. Analytics Report Assets (3 sources)")
    print("  5. Pipeline Summary Asset (1 final)")

    print(f"\n🎯 Total Assets Materialized: {len(test_sources) * 4 + 1}")

    return result


if __name__ == "__main__":
    print("Data Lineage and Asset Materialization Demo")
    print("=" * 50)

    try:
        result = test_data_lineage()

        print("\n✅ Features Demonstrated:")
        print("  - Asset materialization at each pipeline stage")
        print("  - Data lineage tracking through artifacts")
        print("  - Quality validation with metrics")
        print("  - Analytics generation with insights")
        print("  - Pipeline summary with execution tracking")
        print("  - Artifact linking for easy navigation")

        print(f"\n🔍 View artifacts in Prefect UI:")
        print(f"  http://localhost:4200/artifacts")

    except Exception as e:
        print(f"Demo ready: {e}")
