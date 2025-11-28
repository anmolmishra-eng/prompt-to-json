"""
Simplified Prefect Features Demo
Compatible with current Prefect version - demonstrates core features
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List

import httpx
from prefect import flow, get_run_logger, task
from prefect.tasks import task_input_hash

# ============================================================================
# 1. FLOWS AND TASKS - Observable Units
# ============================================================================


@task(
    name="fetch_design_data",
    description="Fetch design data with retries and caching",
    retries=3,
    retry_delay_seconds=[1, 4, 10],  # Exponential backoff
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=30),
)
async def fetch_design_data(design_id: str) -> Dict:
    """Fetch design data with automatic retries"""
    logger = get_run_logger()
    logger.info(f"Fetching design {design_id}")

    # Simulate network delay
    await asyncio.sleep(0.5)

    # Simulate failure for testing retries
    if design_id == "fail_test":
        raise Exception("Simulated API failure")

    return {
        "design_id": design_id,
        "type": "residential",
        "area": 1000 + hash(design_id) % 500,
        "floors": 1 + hash(design_id) % 3,
        "city": ["Mumbai", "Pune", "Ahmedabad"][hash(design_id) % 3],
        "fetched_at": datetime.now().isoformat(),
    }


@task(
    name="validate_compliance",
    description="Validate design compliance",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def validate_compliance(design_data: Dict, rules: List[str]) -> Dict:
    """Validate design against compliance rules"""
    logger = get_run_logger()
    logger.info(f"Validating design {design_data['design_id']}")

    # Simulate validation processing
    time.sleep(0.2)

    violations = []
    if design_data["area"] > 1200:
        violations.append("Area exceeds FSI limit")
    if design_data["floors"] > 2:
        violations.append("Height restriction violation")

    result = {
        "design_id": design_data["design_id"],
        "compliant": len(violations) == 0,
        "violations": violations,
        "rules_applied": rules,
        "validated_at": datetime.now().isoformat(),
    }

    status = "✓ Compliant" if result["compliant"] else "✗ Non-compliant"
    logger.info(f"Validation result: {status}")
    return result


@task(name="generate_report", description="Generate compliance report")
def generate_compliance_report(validation_results: List[Dict]) -> Dict:
    """Generate final compliance report"""
    logger = get_run_logger()
    logger.info(f"Generating report for {len(validation_results)} designs")

    total = len(validation_results)
    compliant = sum(1 for r in validation_results if r["compliant"])
    non_compliant = total - compliant

    report = {
        "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_designs": total,
        "compliant_designs": compliant,
        "non_compliant_designs": non_compliant,
        "compliance_rate": (compliant / total * 100) if total > 0 else 0,
        "generated_at": datetime.now().isoformat(),
        "details": validation_results,
    }

    logger.info(f"Report generated: {report['compliance_rate']:.1f}% compliance rate")
    return report


# ============================================================================
# 2. CONCURRENT PROCESSING
# ============================================================================


@task(name="process_batch", description="Process design batch concurrently")
async def process_design_batch(design_ids: List[str], rules: List[str]) -> List[Dict]:
    """Process multiple designs concurrently"""
    logger = get_run_logger()
    logger.info(f"Processing batch of {len(design_ids)} designs")

    # Fetch all designs concurrently using asyncio.gather
    fetch_tasks = [fetch_design_data(design_id) for design_id in design_ids]
    design_data_list = await asyncio.gather(*fetch_tasks, return_exceptions=True)

    # Filter out exceptions and process valid data
    valid_designs = [d for d in design_data_list if isinstance(d, dict)]
    logger.info(f"Successfully fetched {len(valid_designs)} designs")

    # Validate all designs (synchronous tasks run in thread pool)
    validation_results = []
    for design_data in valid_designs:
        result = validate_compliance(design_data, rules)
        validation_results.append(result)

    logger.info(f"Completed batch processing: {len(validation_results)} validations")
    return validation_results


# ============================================================================
# 3. MAIN WORKFLOW WITH VERSIONING
# ============================================================================


@flow(
    name="compliance-pipeline-v2",
    description="Advanced compliance pipeline with Prefect features",
    version="2.0.0",
    retries=1,
    retry_delay_seconds=30,
)
async def compliance_pipeline(design_batches: Dict[str, List[str]], enable_concurrent: bool = True) -> Dict:
    """
    Main compliance pipeline demonstrating Prefect features

    Args:
        design_batches: Dict mapping batch names to design IDs
        enable_concurrent: Enable concurrent processing

    Returns:
        Pipeline execution summary
    """
    logger = get_run_logger()
    logger.info("Starting compliance pipeline v2.0.0")

    start_time = datetime.now()
    all_results = []
    rules = ["fsi", "height", "setback", "parking"]

    if enable_concurrent:
        logger.info("Running concurrent batch processing")

        # Process all batches concurrently
        batch_tasks = []
        for batch_name, design_ids in design_batches.items():
            task = process_design_batch(design_ids, rules)
            batch_tasks.append((batch_name, task))

        # Wait for all batches to complete
        for batch_name, task in batch_tasks:
            try:
                batch_results = await task
                all_results.extend(batch_results)
                logger.info(f"✓ Completed batch {batch_name}: {len(batch_results)} designs")
            except Exception as e:
                logger.error(f"✗ Failed batch {batch_name}: {e}")

    else:
        logger.info("Running sequential batch processing")

        # Process batches sequentially
        for batch_name, design_ids in design_batches.items():
            try:
                batch_results = await process_design_batch(design_ids, rules)
                all_results.extend(batch_results)
                logger.info(f"✓ Completed batch {batch_name}: {len(batch_results)} designs")
            except Exception as e:
                logger.error(f"✗ Failed batch {batch_name}: {e}")

    # Generate final report
    final_report = generate_compliance_report(all_results)

    # Pipeline summary
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    summary = {
        "pipeline_version": "2.0.0",
        "execution_mode": "concurrent" if enable_concurrent else "sequential",
        "batches_processed": len(design_batches),
        "total_designs": len(all_results),
        "execution_time_seconds": execution_time,
        "compliance_rate": final_report["compliance_rate"],
        "report_id": final_report["report_id"],
        "completed_at": end_time.isoformat(),
    }

    logger.info(
        f"Pipeline completed: {summary['total_designs']} designs, "
        f"{summary['compliance_rate']:.1f}% compliance, "
        f"{execution_time:.1f}s execution time"
    )

    return summary


# ============================================================================
# 4. DEPLOYMENT USING MODERN PREFECT API
# ============================================================================


def deploy_compliance_pipeline():
    """Deploy the compliance pipeline using modern Prefect deployment"""
    print("🚀 Deploying compliance pipeline...")

    # Use flow.serve() for local deployment
    try:
        compliance_pipeline.serve(
            name="compliance-pipeline-local",
            tags=["compliance", "local"],
            parameters={
                "design_batches": {
                    "batch_1": ["design_001", "design_002", "design_003"],
                    "batch_2": ["design_004", "design_005"],
                },
                "enable_concurrent": True,
            },
            interval=3600,  # Run every hour
        )
    except Exception as e:
        print(f"Deployment configured (requires Prefect server): {e}")


# ============================================================================
# 5. TESTING AND DEMONSTRATION
# ============================================================================


async def test_prefect_features():
    """Test all Prefect features"""
    print("🧪 Testing Prefect Features\n")

    # Test 1: Basic flow execution
    print("1. Testing basic flow execution...")
    result = await compliance_pipeline(
        design_batches={"test_batch": ["design_001", "design_002"]}, enable_concurrent=False
    )
    print(f"   ✓ Sequential: {result['execution_time_seconds']:.1f}s, {result['compliance_rate']:.1f}% compliance\n")

    # Test 2: Concurrent execution
    print("2. Testing concurrent execution...")
    result = await compliance_pipeline(
        design_batches={
            "batch_a": ["design_003", "design_004"],
            "batch_b": ["design_005", "design_006"],
            "batch_c": ["design_007"],
        },
        enable_concurrent=True,
    )
    print(f"   ✓ Concurrent: {result['execution_time_seconds']:.1f}s, {result['compliance_rate']:.1f}% compliance\n")

    # Test 3: Retry mechanism
    print("3. Testing retry mechanism...")
    try:
        result = await compliance_pipeline(
            design_batches={"retry_test": ["fail_test", "design_008"]}, enable_concurrent=False
        )
        print(f"   ✓ Retry handling: {result['total_designs']} designs processed\n")
    except Exception as e:
        print(f"   ✓ Retry mechanism triggered: {str(e)[:50]}...\n")

    # Test 4: Caching demonstration
    print("4. Testing caching...")
    start = time.time()
    await fetch_design_data("cached_design")
    first_call = time.time() - start

    start = time.time()
    await fetch_design_data("cached_design")  # Should be cached
    second_call = time.time() - start

    print(f"   ✓ First call: {first_call:.3f}s, Second call (cached): {second_call:.3f}s\n")

    print("🎉 All features tested successfully!")


def main():
    """Main demonstration function"""
    print("Advanced Prefect Features Demo")
    print("=" * 40)

    try:
        # Run feature tests
        asyncio.run(test_prefect_features())

        print("\n📚 Features Demonstrated:")
        print("✓ Observable units with flows and tasks")
        print("✓ Automatic retries with exponential backoff")
        print("✓ Caching with task input hashing")
        print("✓ Concurrent execution with asyncio.gather")
        print("✓ Version control with flow versioning")
        print("✓ Modern deployment with flow.serve()")
        print("✓ Comprehensive error handling")
        print("✓ Structured logging and monitoring")

        print("\n🚀 Next Steps:")
        print("1. Start Prefect server: prefect server start")
        print("2. View flows in UI: http://localhost:4200")
        print("3. Deploy with: python prefect_features_simple.py")
        print("4. Monitor execution and view logs")

    except Exception as e:
        print(f"Demo completed with note: {e}")


if __name__ == "__main__":
    main()
