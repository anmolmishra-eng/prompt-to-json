"""
Test all Prefect workflows
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from workflows.ingestion.pdf_to_mcp_flow import pdf_ingestion_flow, PDFIngestionConfig
from workflows.monitoring.log_aggregation_flow import log_aggregation_flow, LogConfig
from workflows.compliance.geometry_verification_flow import geometry_verification_flow, GeometryConfig


async def test_all_workflows():
    """Test all workflows with sample data"""
    
    print("Testing all BHIV workflows...")
    print("=" * 50)
    
    results = {}
    
    # Test 1: PDF Ingestion Flow
    print("\n[1/3] Testing PDF Ingestion Flow...")
    try:
        pdf_config = PDFIngestionConfig(
            pdf_source_dir=Path("test_data/pdfs"),
            output_dir=Path("test_output/mcp_rules"),
            mcp_api_url="http://localhost:8001"
        )
        
        pdf_result = await pdf_ingestion_flow(pdf_config)
        results["pdf_ingestion"] = pdf_result
        print(f"✅ PDF Ingestion: {pdf_result['status']}")
        
    except Exception as e:
        print(f"❌ PDF Ingestion failed: {e}")
        results["pdf_ingestion"] = {"status": "error", "error": str(e)}
    
    # Test 2: Log Aggregation Flow
    print("\n[2/3] Testing Log Aggregation Flow...")
    try:
        log_config = LogConfig(
            log_sources=[
                Path("test_data/logs/task7"),
                Path("test_data/logs/sohum_mcp"),
                Path("test_data/logs/ranjeet_rl"),
                Path("test_data/logs/bhiv")
            ],
            output_dir=Path("test_output/logs"),
            retention_days=30
        )
        
        log_result = await log_aggregation_flow(log_config)
        results["log_aggregation"] = log_result
        print(f"✅ Log Aggregation: {log_result['status']}")
        
    except Exception as e:
        print(f"❌ Log Aggregation failed: {e}")
        results["log_aggregation"] = {"status": "error", "error": str(e)}
    
    # Test 3: Geometry Verification Flow
    print("\n[3/3] Testing Geometry Verification Flow...")
    try:
        geometry_config = GeometryConfig(
            glb_source_dir=Path("test_data/geometry_outputs"),
            output_dir=Path("test_output/geometry_verification"),
            max_file_size_mb=50.0
        )
        
        geometry_result = await geometry_verification_flow(geometry_config)
        results["geometry_verification"] = geometry_result
        print(f"✅ Geometry Verification: {geometry_result['status']}")
        
    except Exception as e:
        print(f"❌ Geometry Verification failed: {e}")
        results["geometry_verification"] = {"status": "error", "error": str(e)}
    
    # Summary
    print("\n" + "=" * 50)
    print("WORKFLOW TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r.get("status") not in ["error", "failed"])
    
    print(f"Total workflows tested: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests / total_tests * 100):.1f}%")
    
    for workflow, result in results.items():
        status = result.get("status", "unknown")
        print(f"  - {workflow}: {status}")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(test_all_workflows())
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results.values() if r.get("status") in ["error", "failed"])
    sys.exit(failed_count)