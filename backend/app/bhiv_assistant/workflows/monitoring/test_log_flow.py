"""
Test Log Aggregation Workflow
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

from .log_aggregation_flow import LogConfig, log_aggregation_flow


async def test_log_aggregation():
    """Test the log aggregation workflow"""
    print("Testing Log Aggregation Workflow...")

    # Create temporary directories and test log files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create log source directories
        log_sources = []
        for system in ["task7", "sohum_mcp", "ranjeet_rl", "bhiv"]:
            log_dir = temp_path / "logs" / system
            log_dir.mkdir(parents=True)
            log_sources.append(log_dir)

            # Create test log file with errors and warnings
            log_file = log_dir / f"{system}.log"
            log_content = f"""
{datetime.now().isoformat()} INFO Starting {system} service
{datetime.now().isoformat()} WARNING Configuration file not found, using defaults
{datetime.now().isoformat()} INFO Service initialized successfully
{datetime.now().isoformat()} ERROR Failed to connect to database
{datetime.now().isoformat()} INFO Retrying connection...
{datetime.now().isoformat()} ERROR Connection timeout after 30 seconds
{datetime.now().isoformat()} WARNING High memory usage detected
{datetime.now().isoformat()} INFO Service running normally
"""
            log_file.write_text(log_content.strip())
            print(f"Created test log: {log_file}")

        # Create output directory
        output_dir = temp_path / "reports" / "logs"

        # Create test configuration
        config = LogConfig(log_sources=log_sources, output_dir=output_dir, retention_days=30)

        print(f"\nTest configuration:")
        print(f"  Log sources: {len(config.log_sources)} directories")
        print(f"  Output directory: {config.output_dir}")

        try:
            # Run the workflow
            result = await log_aggregation_flow(config)

            print("\nWorkflow Result:")
            print(f"  Status: {result['status']}")
            print(f"  Report file: {result['report_file']}")
            print(f"  Errors found: {result['error_count']}")
            print(f"  Warnings found: {result['warning_count']}")
            print(f"  Alert sent: {result['alert_sent']}")

            # Check if report file was created
            report_path = Path(result["report_file"])
            if report_path.exists():
                print(f"\n[OK] Report file created successfully")
                print(f"   Size: {report_path.stat().st_size} bytes")

                # Show report content
                import json

                with open(report_path) as f:
                    report_data = json.load(f)

                print(f"\nReport Summary:")
                print(f"  Timestamp: {report_data['timestamp']}")
                print(f"  Sources processed: {report_data['sources']}")
                print(f"  Total errors: {report_data['error_summary']['total_errors']}")
                print(f"  Total warnings: {report_data['error_summary']['total_warnings']}")

            return result

        except Exception as e:
            print(f"Workflow failed: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(test_log_aggregation())
    print(f"\nTest completed with status: {result.get('status')}")
