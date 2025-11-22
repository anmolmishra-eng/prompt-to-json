"""
Test Geometry Verification Workflow
"""

import asyncio
import tempfile
from pathlib import Path
from geometry_verification_flow import geometry_verification_flow, GeometryConfig


async def test_geometry_verification():
    """Test the geometry verification workflow"""
    print("Testing Geometry Verification Workflow...")
    
    # Create temporary directories and test GLB files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        glb_dir = temp_path / "geometry_outputs"
        output_dir = temp_path / "reports" / "geometry_verification"
        
        glb_dir.mkdir(parents=True)
        
        # Create test GLB files (dummy files for testing)
        test_files = [
            ("valid_model.glb", b"GLB test content - valid model"),
            ("large_model.glb", b"GLB test content - large model" * 1000),  # Larger file
            ("small_model.glb", b"GLB test content - small"),
        ]
        
        for filename, content in test_files:
            glb_file = glb_dir / filename
            glb_file.write_bytes(content)
            print(f"Created test GLB: {glb_file}")
        
        # Create test configuration
        config = GeometryConfig(
            glb_source_dir=glb_dir,
            output_dir=output_dir,
            max_file_size_mb=0.1  # Small limit for testing
        )
        
        print(f"\nTest configuration:")
        print(f"  GLB source: {glb_dir}")
        print(f"  Output directory: {output_dir}")
        print(f"  Max file size: {config.max_file_size_mb}MB")
        
        try:
            # Run the workflow
            result = await geometry_verification_flow(config)
            
            print("\nWorkflow Result:")
            print(f"  Status: {result['status']}")
            print(f"  Total files: {result['total_files']}")
            print(f"  Report file: {result['report_file']}")
            
            # Check if report file was created
            report_path = Path(result['report_file'])
            if report_path.exists():
                print(f"\n[OK] Report file created successfully")
                print(f"   Size: {report_path.stat().st_size} bytes")
                
                # Show report content
                import json
                with open(report_path) as f:
                    report_data = json.load(f)
                
                print(f"\nVerification Summary:")
                print(f"  Timestamp: {report_data['timestamp']}")
                print(f"  Total files: {report_data['total_files']}")
                print(f"  Passed: {report_data['passed']}")
                print(f"  Failed: {report_data['failed']}")
                print(f"  Errors: {report_data['errors']}")
                print(f"  Pass rate: {report_data['pass_rate']}")
                
                # Show individual results
                print(f"\nFile Results:")
                for file_result in report_data['results']:
                    status = file_result.get('status', 'unknown')
                    filename = file_result.get('filename', 'unknown')
                    print(f"  - {filename}: {status}")
                    if 'issues' in file_result:
                        for issue in file_result['issues']:
                            print(f"    Issue: {issue}")
            
            return result
            
        except Exception as e:
            print(f"Workflow failed: {e}")
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(test_geometry_verification())
    print(f"\nTest completed with status: {result.get('status')}")